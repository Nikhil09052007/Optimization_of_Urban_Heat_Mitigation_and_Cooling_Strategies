# 01_authenticate.py
# Run this ONCE only — saves auth token permanently on your machine
# After this you never need to run it again

import ee

# Force browser-based login
ee.Authenticate(auth_mode='notebook')

# Confirm it worked
ee.Initialize(project='urban-heat-project-499314')
print(ee.String('Authenticated and connected OK').getInfo())
