import subprocess
import os

def spawn_clients(num_instances):
    # Path to the project and virtual environment
    project_dir = os.path.expanduser("~/Documents/SmartMeter/client")
    venv_activate = os.path.join(project_dir, "venv/bin/activate")
    main_script = os.path.join(project_dir, "main.py")

    # Ensure paths exist
    if not os.path.exists(project_dir):
        print(f"Error: Project directory does not exist at {project_dir}")
        return
        
    if not os.path.exists(venv_activate):
        print(f"Error: Virtual environment activation script not found at {venv_activate}")
        return

    if not os.path.exists(main_script):
        print(f"Error: Main script not found at {main_script}")
        return

    processes = []

    try:
        for i in range(num_instances):
            print(f"Spawning instance {i+1}...")

            # Launch a new instance
            process = subprocess.Popen(
                f"source {venv_activate} && python {main_script}",
                shell = True,
                cwd = project_dir,
                executable = "/bin/bash"
            )

            processes.append(process)

        print(f"{num_instances} instances spawned successfully.")
    except Exception as exception:
        print(f"An error occurred: {exception}")
    finally:
        # Wait for all processes to complete
        for process in processes:
            process.wait()

        print("All processes completed.")

if __name__ == "__main__":
    # Specify how many instances to spawn
    instances = int(input("Enter the number of instances to spawn: "))
    spawn_clients(instances)