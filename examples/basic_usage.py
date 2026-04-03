from pysolark import SolArkClient


client = SolArkClient(username="you@example.com", password="***")
client.login()

plant_id = 424242
plant = client.get_plant(plant_id)
realtime = client.get_plant_realtime(plant_id)
flow = client.get_plant_energy_flow(plant_id)

print(f"Plant: {plant.name}")
print(f"Current output (W): {realtime.pac}")
print(f"Battery SOC (%): {flow.soc}")
