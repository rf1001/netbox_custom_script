from extras.scripts import *
from django.utils.text import slugify

from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Site, Region, devices 
from extras.models import Tag
from ipam.models import Prefix

class NewBranchScript(Script):

    class Meta:
        name = "New Site"
        description = "Provision a new branch site"

    site_name = StringVar(
        description="Name of the new site"
    )
    site_region = ObjectVar(
        model=Region,
        required=True,
        description="Select a Region"
    )
    switches = MultiObjectVar(
            required=False,
            model=Device, 
            #queryset=Device.objects.all(),
            query_params={"status" : "inventory", "role_id": 2},
            description="Switches from Inventory"
    )
    firewalls= MultiObjectVar(
            required=False,
            model=Device, 
            query_params={"status" : "inventory", "role_id":1},
            description="Firewalls from Inventory"
    )
    aps= MultiObjectVar(
            required=False,
            model=Device, 
            query_params={"status" : "inventory", "role_id":3},
            description="AccessPoints from Inventory"
    )
    
    def run(self, data, commit):
        # Create a tag 
        temp = data['site_name'].split('-')
        if len(temp) == 3:
            site_tag = temp[0][:2] + "-" + temp[1][:2] + "-" + temp[2][:2]
        if Tag.objects.filter(name=site_tag).exists():
            slef.log_info(f"TAG '{site_tag}' alreay exitst.")
            return
        tag = Tag.objects.create(
                name=site_tag,
                slug=slugify(site_tag)
                )
        # Create the new site
        self.log_success(f"Created tag: {tag.name}")
        Region = data['site_region']
        site = Site(
            name=data['site_name'],
            slug=slugify(data['site_name']),
            region=data['site_region'],
            status=SiteStatusChoices.STATUS_PLANNED
        )
        
        site.save()
        site.tags.add(tag)

        self.log_success(f"Created new site: {site}")
        #Switches = data.get("switches",[])
        s_switches = data['switches']
        count = 1
        for switch in s_switches:
            switch.name = f'{site}-MS-{count}'
            switch.status = DeviceStatusChoices.STATUS_PLANNED
            switch.tags.add(tag)
            switch.site = site
            switch.save()
            self.log_success(f"{switch.name} , {switch.tags}, {switch.site}")
            count += 1
        Firewalls = data['firewalls']
        count = 1
        for firewall in Firewalls:
            firewall.name = f'{site}-MX-{count}'
            firewall.status = DeviceStatusChoices.STATUS_PLANNED
            firewall.tags.add(tag)
            firewall.site = site
            firewall.save()
            self.log_success(f"{firewall.name} , {firewall.tags}, {firewall.site}")
            count += 1
        
        APS = data['aps']
        count = 1
        for ap in APS:
            ap.name = f'{site}-MR-{count}'
            ap.status = DeviceStatusChoices.STATUS_PLANNED
            ap.tags.add(tag)
            ap.site = site
            ap.save()
            self.log_success(f"{ap.name} , {ap.tags}, {ap.site}")
            count += 1
        
        Region = data['site_region']
        prefixes = Prefix.objects.filter(site_region=Region)
        self.log_info(f"Prefixes in region '{Region.name}': ")
        if prefix:
            for prefix in prefixes:
                self.log_success(f"Prefix: {prefix.prefix} (ID: {prefix.id})")
        else:
            self.log_warning("No prefixes found in this region.")
        #region_prefix = Prefix.objects.filter(site_region=Region)
        #self.log_success(f"Assigned Prefix to {region} is {region_prefix}")
        #last_prefix = Prefix.objexts.filter 



         #   if Switches:
        #    updated_count = Switches.update(site=site)
        #    self.log_success(f"Assigned {updated_count} devices to site: {site.name}")
        #else:
        #    self.log_warning("No devices selected.")