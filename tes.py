import torch
print(torch.version.cuda)  # Harus '12.8'
print(torch.cuda.get_arch_list())  # Harus mencakup 'sm_120'
