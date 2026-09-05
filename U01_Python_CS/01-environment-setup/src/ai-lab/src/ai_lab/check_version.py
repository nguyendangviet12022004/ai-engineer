def check_pkg(module_name: str) -> str:
  module = __import__(module_name)
  return getattr(module, "__version__", "No versions")

def check_device():
  try:
    import torch 
    if torch.cuda.is_available():
        # 2. Get the total number of available GPUs
        gpu_count = torch.cuda.device_count()
        print(f"Total GPUs available: {gpu_count}")
        
        # 3. Loop through and get the name of each GPU
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            print(f"GPU {i}: {gpu_name}")
    else:
        print("CUDA is not available. Running on CPU.")
  except ImportError:
      print("You haven't installed torch")