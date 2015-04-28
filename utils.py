import boto.ec2
import boto.utils
import jinja2
import time

instance_metadata = boto.utils.get_instance_metadata()
instance_id       = instance_metadata.get('instance-id')
placement         = instance_metadata.get('placement')
availability_zone = placement.get('availability-zone')
region            = availability_zone[:-1]
connection        = boto.ec2.connect_to_region(region) # TODO, we can change region
local_ipv4s       = instance_metadata.get('local-ipv4s')

def master(id, requester):
    try:
        with open('%s.json' % id, 'r') as f:
            meta = json.load(f)
            # user_data from template
            j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
            USER_DATA = j2_env.get_template('master.user_data').render(local_ipv4s=local_ipv4s, id=id)
            # create a NetworkInterface in our VPC (with public IP)
            interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
                subnet_id                   = meta['SUBNET_ID'],
                groups                      = meta['SECURITY_GROUP_IDS'],
                associate_public_ip_address = True # TODO: don't need public IP
            )
            interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
            # reserve an instance for MASTER node
            reservation = connection.run_instances(
                image_id = meta['IMAGE_ID'],
                key_name = meta['KEY_NAME'],
                user_data = USER_DATA,
                instance_type = meta['INSTANCE_TYPE'],
                instance_initiated_shutdown_behavior = 'terminate',
                #placement_group=PLACEMENT_GROUP, # only for high level machines, not for testing
                network_interfaces = interfaces,
                instance_profile_name = meta['IAM_ROLE']
            )
            for instance in reservation.instances:
                status = instance.update()
                while status == 'pending':
                    time.sleep(5)
                    status = instance.update()
                # -- tags
                instance.add_tag('Name', meta['INSTANCE_NAME'])
                instance.add_tag('REQUESTER', requester)
                #instance.add_tag("ENVIRONMENT", DEPLOYMENT_ENVIRONMENT) # DEVELOPMENT/INTEGRATION/STAGING/PRODUCTION
                print status
                # after up and running, log in something, not sure yet what
                if status == 'running':
                    pass
                else:
                    pass
    except:
        pass
