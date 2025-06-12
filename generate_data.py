from faker import Faker
import pandas as pd
import random 
import os

# set up the fake data generator
fake = Faker()

def ensure_data_directory():
    """Create the data directory if it doesn't exist."""
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(parent_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def generate_patient_data(number_of_patients=1000):
    """
    Generate 1,000 Patient Demographic Data to data/patients_data.csv

    * patient_id -> unique identifier (eg: PT12345)
    * first_name -> eg: John
    * last_name -> eg: Doe
    * dob -> eg: 1875-12-03
    * gender -> eg: Male
    * phone -> eg: 233-245-242-798
    * email -> eg: john.doe@example.com
    * updated_at -> eg: TIMESTAMP = YYYY-MM-DD-HH-MM-SS
"""

    prefixes = ["024", "054", "055", "059", "020", "050"]

    for i in range(1, number_of_patients + 1):
        yield {
            'patient_id' : f"PT{i:04d}",
            'first_name' : fake.first_name(),
            'last_name' : fake.last_name(),
            'date_of_birth' : fake.date_of_birth(minimum_age=18, maximum_age=100),
            'gender' : random.choice(['Male', 'Female']),
            'phone_number' : f"+233{random.choice(prefixes)}{fake.numerify('#######')}",
            'address' : fake.address().replace('\n', ', '),
            'blood_type' : random.choice(['A+', 'B+', 'A-', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            'insurance_number' : f"INS{fake.unique.random_int(min=1000000, max=9999999)}",
            'updated_at' : fake.date_time_this_decade()
        }



def generate_billing_data(number_of_bills=2500):
    """
    Generate 2,500 Billing Data for Patients
    
    * invoice_id -> unique identifier (eg: INV101) 
    * patient_id -> foreign key from patients demographics
    * service_code -> type of service (eg: CONSULT, etc)
    * amount -> eg: 100.00
    * payment_status -> eg: Paid, Unpaid, etc
    * updated_at -> TIMESTAMP
    """
    for i in range(1, number_of_bills + 1):
        yield {
            'invoice_id' : f"INV{i:04d}",
            'patient_id' : f"PT{random.randint(1,1000):04d}",
            'service_code' : random.choice(['CONSULT', 'SURGERY', 'DIAGNOSTICS', 'MEDICATION', 'LAB_TEST', 'IMAGING', 'OTHER']),
            'amount' : round(random.uniform(10, 1000), 2),
            'payment_status' : random.choice(['Paid', 'Unpaid', 'Partially Paid']),
            'updated_at' : fake.date_time_this_decade()
        }



def generate_appointment_data(number_of_appointments=1500):
    """
    Generate 2,000 Patients Appointment Data
    
    * appointment_id -> primary key (eg: APPT189)
    * patient_id -> foreign key for patient id
    * doctor_id -> eg: DR456
    * appointment_date -> time and date scheduled
    * status -> eg: confirmed, etc
    * no_show -> eg: Yes or No (0, 1)
    * patient_name -> eg: John Doe
    """
    for i in range(1, number_of_appointments + 1):
        yield {
            'appointment_id' : f"APPT{i:04d}",
            'patient_id' : f"PT{random.randint(1, 1000):04d}",
            'doctor_id' : f"DR{random.randint(1, 100):03d}",
            'appointment_date' : fake.date_time_this_decade(),
            'status' : random.choice(['Confirmed', 'Cancelled', 'Pending']),
            'no_show' : random.choice(['Yes', 'No'])
        }



def generate_prescription_data(number_of_prescriptions=2500):
    """
    Generate 3,0000 pharmacy data
    
    * prescription_id -> eg: RX1234
    * patient_id -> eg: PT12345
    * doctor_id -> which doctor prescribed the drug
    * drug_id -> eg: MED123
    * drug_name -> name of the drug (eg: Paracetamol 500mg)
    * dosage -> '2 pills everyday'
    * dispensed_date
    """
    for i in range(1, number_of_prescriptions + 1):
        yield {
            'prescription_id' : f'RX{i:04d}',
            'patient_id' : f"PT{random.randint(1, 1000):04d}",
            'doctor_id' : f"DR{random.randint(1, 100):03d}",
            'drug_id' : f"MED{random.randint(1, 1000):04d}",
            'drug_name' : random.choice([
                'Alprazolam', 'Amlodipine', 'Amoxicillin', 'Azithromycin',
                'Baclofen', 'Cardicillin', 'Cardidol', 'Cardidone',
                'Cardimox', 'Cardipam', 'Cardipril', 'Cardisartan',
                'Cardithiazide', 'Cardizol', 'Cardizole', 'Cefcillin',
                'Cefdone', 'Cefline', 'Cefmox', 'Cefpam',
                'Cefsartan', 'Cefstatin', 'Cefthiazide', 'Cefzol',
                'Cetirizine', 'Ciprofloxacin', 'Clonazepam', 'Clopidogrel',
                'Dexamethasone', 'Diazepam', 'Dolocillin', 'Dolodol',
                'Dololine', 'Dolomox', 'Dolopam', 'Dolopril',
                'Dolostatin', 'Dolothiazide', 'Dolozol', 'Dolozole',
                'Fluoxetine', 'Furosemide', 'Gabapentin', 'Gebacillin',
                'Gebadone', 'Gebaline', 'Gebamox', 'Gebapam',
                'Gebasartan', 'Gebastatin', 'Gebathiazide', 'Gebazol',
                'Hemacillin', 'Hemadol', 'Hemadone', 'Hemaline',
                'Hemapam', 'Hemapril', 'Hemasartan', 'Hemastatin',
                'Hemazol', 'Hemazole', 'Hydrochlorothiazide', 'Ibuprofen',
                'Lisinopril', 'Loracillin', 'Loradol', 'Loradone',
                'Loramox', 'Lorapam', 'Lorapril', 'Lorasartan',
                'Loratadine', 'Lorathiazide', 'Lorazol', 'Lorazole',
                'Meloxicam', 'Metformin', 'Metoprolol', 'Naproxen',
                'Neurodol', 'Neurodone', 'Neuroline', 'Neuromox',
                'Neuropril', 'Neurosartan', 'Neurostatin', 'Neurothiazide',
                'Neurozole', 'Omeprazole', 'Oxacillin', 'Oxadol',
                'Oxaline', 'Oxamox', 'Oxapam', 'Oxapril',
                'Oxastatin', 'Oxathiazide', 'Oxazol', 'Oxazole',
                'Paracetamol', 'Prednisone', 'Propranolol', 'Ranitidine',
                'Rivacillin', 'Rivadol', 'Rivadone', 'Rivaline',
                'Rivapam', 'Rivapril', 'Rivasartan', 'Rivastatin',
                'Rivazol', 'Rivazole', 'Sertraline', 'Simvastatin',
                'Tramadol', 'Tramadone', 'Tramaline', 'Tramamox',
                'Tramapril', 'Tramasartan', 'Tramastatin', 'Tramathiazide',
                'Tramazole', 'Vaxacillin', 'Vaxadol', 'Vaxadone',
                'Vaxamox', 'Vaxapam', 'Vaxapril', 'Vaxasartan',
                'Vaxathiazide', 'Vaxazol', 'Vaxazole', 'Xenocillin',
                'Xenodone', 'Xenoline', 'Xenomox', 'Xenopam',
                'Xenosartan', 'Xenostatin', 'Xenothiazide', 'Xenozol',
                'Zanodol', 'Zanodone', 'Zanoline', 'Zanomox',
                'Zanopril', 'Zanosartan', 'Zanostatin', 'Zanothiazide',
                'Zanozole', 'Zolpidem'
            ]),
            'dosage' : random.choice([
                "Apply a thin layer to the affected area once daily",
                "Inhale 2 puffs every 4 hours",
                "Take 1 capsule every 12 hours",
                "Take 1 capsule twice a day", 
                "Take 1 drop in each eye twice daily",
                "Take 1 pill after meals",
                "Take 1 suppository at bedtime",
                "Take 1 tablet as needed for pain",
                "Take 1 tablet before bedtime",
                "Take 1 tablet before meals",
                "Take 1 tablet every morning",
                "Take 1 tablet every other day",
                "Take 1 tablet once daily",
                "Take 1 tablet on an empty stomach",
                "Take 1 tablet with food",
                "Take 2 capsules once daily",
                "Take 2 tablets every 6 hours",
                "Take 5 mL once at night",
                "Take 5 mL three times a day",
                "Take 10 mL every 8 hours"
            ]),
            'dispensed_date' : fake.date_time_this_decade()
        }



def generate_inventory_items(number_of_items=500):
    """
    Generate 500 inventory items for restocking

    * item_id -> primary key (eg: STR190)
    * name -> name of item (eg: Syringe 50mL)
    * quantity -> number of items left (eg: 200)
    * reorder_level -> level for restocking (eg: 50)
    * supplier -> supplier of medicine (eg: MediCorp, Tobinco, Ernest Chemist)
    * updated_at -> TIMESTAMP
    """
    for i in range(1, number_of_items + 1):
        yield {
            'item_id' : f'STR{i:03d}',
            'item_name' : fake.word(),
            'quantity' : random.randint(1, 500),
            'reorder_level' : random.randint(50, 100),
            'supplier': random.choice(["Ernest Chemists Limited", "Kinapharma Limited", 
                                       "Dannex Ayrton Starwin PLC", "Pharmanova Limited", 
                                       "LaGray Chemical Company", "Pfizer Inc.",
                                       "GlaxoSmithKline (GSK)", "Roche Holding AG"]),
            'updated_at': fake.date_time_this_decade()
        }



# Helper function to save generator data to CSV
def save_generator_to_csv(generator_func, output_file, **kwargs):
    df = pd.DataFrame(generator_func(**kwargs))
    df.to_csv(output_file, index=False)
    return df

# Example usage:
if __name__ == "__main__":
    # Ensure data directory exists
    data_dir = ensure_data_directory()
    
    # Generate and save all data
    save_generator_to_csv(generate_patient_data, os.path.join(data_dir, 'patients_data.csv'))
    save_generator_to_csv(generate_billing_data, os.path.join(data_dir, 'billing_data.csv'))
    save_generator_to_csv(generate_appointment_data, os.path.join(data_dir, 'appointments_data.csv'))
    save_generator_to_csv(generate_prescription_data, os.path.join(data_dir, 'prescriptions_data.csv'))
    save_generator_to_csv(generate_inventory_items, os.path.join(data_dir, 'inventory_items.csv'))



