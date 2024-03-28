from prefect import flow

@flow(log_prints=True)
def cloud_run_job_flow():
    print("Hello, Prefect!")

#if __name__ == "__main__":
#    cloud_run_job_flow()