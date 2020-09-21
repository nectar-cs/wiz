import re

experiment = "$(right) $() of $(the-bat) we $(have/one) not $fakes"

result = re.findall(r"\$\((.*?)\)", experiment)

result2 = re.finditer(r"\$\((.*?)\)", experiment)

r3 = re.search(r"\$\((.*?)\)", experiment)



