import logging
from datetime import datetime
from etl.utils.logger import setup_logger
from etl.pipelines.patients_pipeline import run_pipeline as run_patients_pipeline
from etl.pipelines.billing_pipeline import run_pipeline as run_billing_pipeline
from etl.pipelines.appointments_pipeline import run_pipeline as run_appointments_pipeline
from etl.pipelines.prescriptions_pipeline import run_pipeline as run_prescriptions_pipeline
from etl.pipelines.inventory_pipeline import run_pipeline as run_inventory_pipeline

# Setup main orchestration logger
logger = setup_logger('pipeline_orchestrator')

def run_all_pipelines():
    """
    Run all ETL pipelines in sequence.
    Order:
    1. Patients (core demographic data)
    2. Billing (financial data)
    3. Appointments (scheduling data)
    4. Prescriptions (medical data)
    5. Inventory (stock management)
    """
    start_time = datetime.now()
    failed_pipelines = []
    
    # Dictionary of pipelines with their names and functions
    pipelines = {
        'patients': run_patients_pipeline,
        'billing': run_billing_pipeline,
        'appointments': run_appointments_pipeline,
        'prescriptions': run_prescriptions_pipeline,
        'inventory': run_inventory_pipeline
    }
    
    logger.info("Starting HMS data pipeline orchestration")
    logger.info(f"Pipelines to run: {', '.join(pipelines.keys())}")
    
    # Run each pipeline and track success/failure
    for name, pipeline_func in pipelines.items():
        pipeline_start = datetime.now()
        logger.info(f"Starting {name} pipeline")
        
        try:
            pipeline_func()
            duration = datetime.now() - pipeline_start
            logger.info(f"Successfully completed {name} pipeline in {duration}")
            
        except Exception as e:
            duration = datetime.now() - pipeline_start
            logger.error(f"Failed to run {name} pipeline after {duration}: {str(e)}")
            failed_pipelines.append(name)
            # Continue with next pipeline despite failure
            continue
    
    # Log final summary
    total_duration = datetime.now() - start_time
    logger.info(f"Pipeline orchestration completed in {total_duration}")
    
    if failed_pipelines:
        logger.error(f"The following pipelines failed: {', '.join(failed_pipelines)}")
        logger.error(f"Please check individual pipeline logs for detailed error information")
        return False
    else:
        logger.info("All pipelines completed successfully!")
        return True

if __name__ == "__main__":
    try:
        success = run_all_pipelines()
        exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"Critical error in pipeline orchestration: {str(e)}")
        exit(1) 