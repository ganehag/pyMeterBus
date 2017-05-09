def is_primary_address(value):
  return 0x00 <= value <= 0xFF


def is_secondary_address(value):
  if value == None:
    return False

  if len(value) != 16:
    return False

  try:
    _ = int(value, 16)
  except ValueError:
    return False

  return True
