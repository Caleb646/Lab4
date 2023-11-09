import boto3
import json
import random
import string
import os

thingArn = ""
thingId = ""
thingName = ""
defaultPolicyName = "CS_437_Thing"

def create_thing():
	global thing_client, thingName, thingArn, defaultPolicyName
	thingName = "".join([random.choice(string.ascii_letters + string.digits) for n in range(25)])
	thingResponse = thing_client.create_thing(thingName = thingName)
	data = json.loads(json.dumps(thingResponse, sort_keys=False, indent=4))
	for element in data: 
		if element == 'thingArn':
			thingArn = data['thingArn']
		elif element == 'thingId':
			thingId = data['thingId']
	createCertificate()

def createCertificate():
	global thing_client, thingName, thingArn, defaultPolicyName
	certResponse = thing_client.create_keys_and_certificate(setAsActive=True)
	data = json.loads(json.dumps(certResponse, sort_keys=False, indent=4))
	for element in data: 
		if element == 'certificateArn':
			certificateArn = data['certificateArn']
		elif element == 'keyPair':
			PublicKey = data['keyPair']['PublicKey']
			PrivateKey = data['keyPair']['PrivateKey']
		elif element == 'certificatePem':
			certificatePem = data['certificatePem']
		elif element == 'certificateId':
			certificateId = data['certificateId']
	os.makedirs(f'./certs/{thingName}/', exist_ok=True)				
	with open(f'./certs/{thingName}/public.key', 'x') as outfile:
			outfile.write(PublicKey)
	with open(f'./certs/{thingName}/private.key', 'x') as outfile:
			outfile.write(PrivateKey)
	with open(f'./certs/{thingName}/cert.pem', 'x') as outfile:
			outfile.write(certificatePem)

	response = thing_client.attach_policy(
			policyName = defaultPolicyName,
			target = certificateArn
	)
	response = thing_client.attach_thing_principal(
			thingName = thingName,
			principal = certificateArn
	)
	response = thing_client.add_thing_to_thing_group(
			thingGroupName="CS437_Thing_Group",
			thingGroupArn="arn:aws:iot:us-east-1:174768554553:thinggroup/CS437_Thing_Group",
			thingName=thingName,
			thingArn=thingArn,
			overrideDynamicGroups=True
	)   
	
if __name__ == "__main__":
	thing_client = boto3.client('iot')
	create_thing()