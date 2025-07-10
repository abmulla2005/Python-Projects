from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field, validator
from typing import Annotated, Literal, Optional
import json
import os

app = FastAPI()

if not os.path.exists("patients.json"):
    with open("patients.json", "w") as f:
        json.dump({}, f)

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", examples=["P001"])] 
    name: Annotated[str, Field(..., description="Name of the Patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., gt=0, le=120, description="Age of the patient")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kgs")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None, description="Name of the Patient")]
    city: Annotated[Optional[str], Field(default=None, description="City where the patient is living")]
    age: Annotated[Optional[int], Field(default=None, gt=0, le=120, description="Age of the patient")]
    gender: Annotated[Optional[Literal["male", "female", "others"]], Field(default=None, description="Gender of the patient")]
    height: Annotated[Optional[float], Field(default=None, gt=0, description="Height of the patient in meters")]
    weight: Annotated[Optional[float], Field(default=None, gt=0, description="Weight of the patient in kgs")]

def load_data():
    try:
        with open("patients.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def api_root():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {
        "message": "A fully functional API to manage your patient records",
        "features": [
            "Create, read, update, and delete patient records",
            "Calculate BMI and health verdict automatically",
            "Sort patients by different metrics"
        ]
    }

@app.get("/view")
def view_all_patients():
    """View all patient records"""
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(
    patient_id: str = Path(..., description="ID of the patient in the DB", example="P001")
):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Patient not found",
                "suggestion": "Check the patient ID or create a new patient"
            }
        )
    return data[patient_id]

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Field to sort by (height, weight, or bmi)"),
    order: str = Query("asc", description="Sort order (asc or desc)")
):
    valid_fields = ["height", "weight", "bmi"]
    
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid sort field '{sort_by}'",
                "valid_fields": valid_fields
            }
        )
    
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid sort order",
                "valid_orders": ["asc", "desc"]
            }
        )
    
    data = load_data()
    patients = list(data.values())
    
    # Add computed fields to each patient
    for patient in patients:
        patient["bmi"] = round(patient["weight"] / (patient["height"] ** 2), 2)
    
    reverse_sort = order == "desc"
    sorted_patients = sorted(patients, key=lambda x: x[sort_by], reverse=reverse_sort)
    
    return sorted_patients

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    
    if patient.id in data:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Patient already exists",
                "suggestion": "Use PUT /edit/{patient_id} to update the patient"
            }
        )
    
    # Store without the ID in the data (using ID as key)
    patient_data = patient.model_dump(exclude=["id"])
    data[patient.id] = patient_data
    save_data(data)
    
    return JSONResponse(
        status_code=201,
        content={
            "message": "Patient created successfully",
            "patient_id": patient.id,
            "bmi": patient.bmi,
            "verdict": patient.verdict
        }
    )

@app.put("/edit/{patient_id}")
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate
):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Patient not found",
                "suggestion": "Check the patient ID or create a new patient"
            }
        )
    
    existing_data = data[patient_id]
    update_data = patient_update.model_dump(exclude_unset=True)
    
    # Apply updates
    for field, value in update_data.items():
        existing_data[field] = value
    
    # Create temporary Patient object to compute BMI and verdict
    temp_patient = Patient(id=patient_id, **existing_data)
    
    # Update the stored data with computed fields
    existing_data["bmi"] = temp_patient.bmi
    existing_data["verdict"] = temp_patient.verdict
    
    save_data(data)
    
    return {
        "message": "Patient updated successfully",
        "patient_id": patient_id,
        "updated_fields": list(update_data.keys()),
        "bmi": temp_patient.bmi,
        "verdict": temp_patient.verdict
    }

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Patient not found",
                "suggestion": "Check the patient ID"
            }
        )
    
    del data[patient_id]
    save_data(data)
    
    return {
        "message": "Patient deleted successfully",
        "patient_id": patient_id
    }