def is_primary_address(value):
  try:
    if type(value) == str:
      value = int(value)
  except ValueError:
    return False
  return 0x00 <= value <= 0xFF

def is_secondary_address(value):
  if value == None:
    return False

  if not isinstance(value, str):
    return False

  if len(value) != 16:
    return False

  try:
    _ = int(value, 16)
  except ValueError:
    return False

  return True

def manufacturer_id(manufacturer):
  if len(manufacturer) != 3:
    return False

  if not manufacturer.isalpha():
    return False

  manufacturer = manufacturer.upper()
  id = ((ord(manufacturer[0]) - 64) * 32 * 32 +
        (ord(manufacturer[1]) - 64) * 32 +
        (ord(manufacturer[2]) - 64))

  if 0x0421 <= id <= 0x6b5a:
    return id

  return False

def manufacturer_encode(value, size):
  if value is None or value == False:
    return None

  data = []
  for i in range(0, size):
    data.append((value>>(i*8)) & 0xFF)

  return data


def inter_byte_timeout(baudrate):
  return {
    300: 0.12,
    600: 0.60,
    1200: 0.4,
    2400: 0.2,
    4800: 0.2,
    9600: 0.1,
    19200: 0.1,
    38400: 0.1,
  }.get(baudrate, None)
