def salmon(s):
  return u"\u001b[38;5;232;48;5;210m{}\u001b[0m".format(s)

def teal(s):
  return u"\u001b[38;5;232;48;5;6m{}\u001b[0m".format(s)

def pink(s):
  return u"\u001b[38;5;232;48;5;165m{}\u001b[0m".format(s)

def white(s):
  return u"\u001b[38;5;232;48;5;250m{}\u001b[0m".format(s)

def grey(s):
  #                    FGC      BGC
  return u"\u001b[38;5;232;48;5;246m{}\u001b[0m".format(s)

def blue(s):
  return u"\u001b[44;1m{}\u001b[0m".format(s)

def green(s):
  return u"\u001b[38;5;232;48;5;40m{}\u001b[0m".format(s)

def yellow(s):
  return u"\u001b[38;5;232;48;5;226m{}\u001b[0m".format(s)

def red(s):
  return u"\u001b[38;5;232;48;5;124m{}\u001b[0m".format(s)

def list_colors():
  import sys
  esc = u"\u001b[0m"
  for i in range(0, 16):
    for j in range(0, 16):
      code = str(i * 16 + j)
      sys.stdout.write(u"\u001b[48;5;" + code + "m " + code.ljust(4))
  print u"\u001b[0m"
