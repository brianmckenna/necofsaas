import boto.ec2
import boto.utils
import jinja2
import json
import time

# EC2 Instance metadata
instance_metadata = boto.utils.get_instance_metadata(timeout=5, num_retries=1)
instance_id       = instance_metadata.get('instance-id')
placement         = instance_metadata.get('placement')
availability_zone = placement.get('availability-zone')
region            = availability_zone[:-1]
connection        = boto.ec2.connect_to_region(region) # TODO, we can change region
local_ipv4        = instance_metadata.get('local-ipv4') # TODO: get port the Flask application is running on

def create_master(id, requester):

    try:

        # -- load configuration data via JSON
        with open('%s.json' % id, 'r') as f:
            config = json.load(f)

            # user_data (cloud-init) from template
            jinja2_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
            USER_DATA = jinja2_environment.get_template('master.user_data').render(local_ipv4=local_ipv4, id=id)

            # create a NetworkInterface in our VPC
            interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
                subnet_id                   = config['SUBNET_ID'],
                groups                      = config['SECURITY_GROUP_IDS'],
                associate_public_ip_address = True # TODO: don't need public IP, for DEBUG
            )
            interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)

            # create the Instance reservation
            reservation = connection.run_instances(
                image_id = config['IMAGE_ID'],
                key_name = config['KEY_NAME'],
                user_data = USER_DATA,
                instance_type = config['MASTER_INSTANCE_TYPE'],
                instance_initiated_shutdown_behavior = 'terminate',
                placement_group = config['PLACEMENT_GROUP'],
                network_interfaces = interfaces,
                instance_profile_name = config['IAM_ROLE']
            )

            # -- loop until instance is running and update tags
            for instance in reservation.instances:
                status = instance.update()
                while status == 'pending':
                    time.sleep(5)
                    status = instance.update()
                instance.add_tag('Name', config['INSTANCE_NAME'])
                instance.add_tag('REQUESTER', requester)


            return reservation

    except:
         # -- notify user of failed process
        pass
