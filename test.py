import boto.ec2
import boto.utils
import jinja2
import time

'''
This is basically going to be a Flask app to kick off NECOFS, but in the meantime, use a script
Should create a machine, and send in 'user_data' to use an script, private on S3, to iniate the master node of a system
That system can then create more nodes as needed (by version)
'''

instance_metadata = boto.utils.get_instance_metadata()
instance_id       = instance_metadata.get('instance-id')
placement         = instance_metadata.get('placement')
availability_zone = placement.get('availability-zone')
region            = availability_zone[:-1]
connection        = boto.ec2.connect_to_region(region) # TODO, we can change region

#iam = boto.connect_iam()
#instance_profile = iam.create_instance_profile('INSTANCE_PROFILE')
#iam.add_role_to_instance_profile('INSTANCE_PROFILE', 'NECOFS')

# WHAT WE WANT TO PROVISION
REQUESTER = '@brianmckenna'
# TODO:
#     get out of database for selected run/version
#IMAGE_ID           = 'ami-146e2a7c' # Amazon Linux AMI 2014.09.2 (HVM) # TODO: use DB for this
#INSTANCE_TYPE      = 'm3.medium'
#PLACEMENT_GROUP    = 'FVCOM' # TODO: use DB for this
#SECURITY_GROUP_IDS = ['sg-54541b30']
#VPC_ID             = 'vpc-79b0e61c'
#SUBNET_ID          = 'subnet-52bc3c0b'
#IAM_ROLE           = 'NECOFS'
#INSTANCE_NAME      = 'Tom "Iceman" Kazanski' # For AWS management purposes, should be a string to help identify which run this is, maybe by date





# load user_data from template
# TODO: pass in the PROVISION data, to be passed to the general MOUNT python script
j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
USER_DATA = j2_env.get_template('master.user_data').render(test='data') # TODO use the dictionary from the JSON file

# create a NetworkInterface in our VPC (with public IP)
interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
    subnet_id                   = SUBNET_ID,
    groups                      = SECURITY_GROUP_IDS,
    associate_public_ip_address = True # TODO: don't need public IP
)
interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)

# reserve an instance for MASTER node
reservation = connection.run_instances(
    image_id=IMAGE_ID,
    key_name=KEY_NAME,
    user_data=USER_DATA,
    instance_type=INSTANCE_TYPE,
    instance_initiated_shutdown_behavior='terminate',
#    placement_group=PLACEMENT_GROUP, # only for high level machines, not for testing
    network_interfaces=interfaces,
    instance_profile_name=IAM_ROLE
)
for instance in reservation.instances:
    status = instance.update()
    while status == 'pending':
        time.sleep(5)
        status = instance.update()
    # -- tags
    instance.add_tag('Name', INSTANCE_NAME)
    instance.add_tag('REQUESTER', REQUESTER)
    #instance.add_tag("ENVIRONMENT", DEPLOYMENT_ENVIRONMENT) # DEVELOPMENT/INTEGRATION/STAGING/PRODUCTION

print status
# after up and running, log in something, not sure yet what
if status == 'running':
    pass
else:
    pass

