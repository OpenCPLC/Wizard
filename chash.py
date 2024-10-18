def hash_string(string:str) -> int:
  hash_value = 5381
  for char in string:
    hash_value = ((hash_value << 5) + hash_value) + ord(char)
  return hash_value & 0xFFFFFFFF

def c_code_enum(hash_list:list[str], title:str="") -> str:
  if title: title = "".join(char for char in title.upper() if char.isalpha()) + "_Hash_"
  else: title = "HASH_"
  c_code = "\ntypedef enum {\n"
  for name in hash_list:
    value = hash_string(name.lower())
    name = name.title()
    name = ''.join(char for char in name if char.isalpha())
    c_code += "  " + title + name + " = " + str(value) + ",\n"
  c_code += "} " + title + "e;\n"
  return c_code
