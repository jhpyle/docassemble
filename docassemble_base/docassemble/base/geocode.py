from docassemble.base.logger import logmessage

class GeoCoder:
    def __init__(self, *args, **kwargs):
        self.server = kwargs['server']
    def geocode(self, *pargs, **kwargs):
        self.data = self.geocoder.geocode(*pargs, **kwargs)
        return True

class GoogleV3GeoCoder(GeoCoder):
    def config_ok(self):
        try:
            assert isinstance(self.server.daconfig['google']['api key'], str)
        except:
            logmessage("geocode: cannot geocode without an 'api key' under 'google' in the Configuration. Set 'geolocate service' in the Configuration to use a different geocoding service.")
            return False
        return True
    def initialize(self):
        from geopy.geocoders import GoogleV3
        self.geocoder = GoogleV3(api_key=self.server.daconfig['google']['api key'])
    def populate_address(self, address):
        if 'formatted_address' in self.data.raw:
            address.one_line = self.data.raw['formatted_address']
            address.norm.one_line = self.data.raw['formatted_address']
            address.norm_long.one_line = self.data.raw['formatted_address']
        if 'address_components' in self.data.raw:
            geo_types = {
                'administrative_area_level_1': ('state', 'short_name'),
                'administrative_area_level_2': ('county', 'long_name'),
                'administrative_area_level_3': ('administrative_area_level_3', 'long_name'),
                'administrative_area_level_4': ('administrative_area_level_4', 'long_name'),
                'administrative_area_level_5': ('administrative_area_level_5', 'long_name'),
                'colloquial_area': ('colloquial_area', 'long_name'),
                'country': ('country', 'short_name'),
                'floor': ('floor', 'long_name'),
                'intersection': ('intersection', 'long_name'),
                'locality': ('city', 'long_name'),
                'neighborhood': ('neighborhood', 'long_name'),
                'post_box': ('post_box', 'long_name'),
                'postal_code': ('postal_code', 'long_name'),
                'postal_code_prefix': ('postal_code_prefix', 'long_name'),
                'postal_code_suffix': ('postal_code_suffix', 'long_name'),
                'postal_town': ('postal_town', 'long_name'),
                'premise': ('premise', 'long_name'),
                'room': ('room', 'long_name'),
                'route': ('street', 'short_name'),
                'street_number': ('street_number', 'short_name'),
                'sublocality': ('sublocality', 'long_name'),
                'sublocality_level_1': ('sublocality_level_1', 'long_name'),
                'sublocality_level_2': ('sublocality_level_2', 'long_name'),
                'sublocality_level_3': ('sublocality_level_3', 'long_name'),
                'sublocality_level_4': ('sublocality_level_4', 'long_name'),
                'sublocality_level_5': ('sublocality_level_5', 'long_name'),
#                    'subpremise': ('unit', 'long_name'),
            }
            for component in self.data.raw['address_components']:
                if 'types' in component and 'long_name' in component:
                    for geo_type, addr_type in geo_types.items():
                        if geo_type in component['types'] and ((not hasattr(address, addr_type[0])) or getattr(address, addr_type[0]) == '' or getattr(address, addr_type[0]) is None):
                            setattr(address, addr_type[0], component[addr_type[1]])
                    if (not hasattr(address, geo_type)) or getattr(address, geo_type) == '' or getattr(address, geo_type) is None:
                        setattr(address, geo_type, component['long_name'])
            geo_types = {
                'administrative_area_level_1': 'state',
                'administrative_area_level_2': 'county',
                'administrative_area_level_3': 'administrative_area_level_3',
                'administrative_area_level_4': 'administrative_area_level_4',
                'administrative_area_level_5': 'administrative_area_level_5',
                'colloquial_area': 'colloquial_area',
                'country': 'country',
                'floor': 'floor',
                'intersection': 'intersection',
                'locality': 'city',
                'neighborhood': 'neighborhood',
                'post_box': 'post_box',
                'postal_code': 'postal_code',
                'postal_code_prefix': 'postal_code_prefix',
                'postal_code_suffix': 'postal_code_suffix',
                'postal_town': 'postal_town',
                'premise': 'premise',
                'room': 'room',
                'route': 'street',
                'street_number': 'street_number',
                'sublocality': 'sublocality',
                'sublocality_level_1': 'sublocality_level_1',
                'sublocality_level_2': 'sublocality_level_2',
                'sublocality_level_3': 'sublocality_level_3',
                'sublocality_level_4': 'sublocality_level_4',
                'sublocality_level_5': 'sublocality_level_5',
#                    'subpremise': 'unit'
            }
            for component in self.data.raw['address_components']:
                if 'types' in component:
                    for geo_type, addr_type in geo_types.items():
                        if geo_type in component['types']:
                            if 'short_name' in component:
                                setattr(address.norm, addr_type, component['short_name'])
                                if addr_type != geo_type:
                                    setattr(address.norm, geo_type, component['short_name'])
                            if 'long_name' in component:
                                setattr(address.norm_long, addr_type, component['long_name'])
                                if addr_type != geo_type:
                                    setattr(address.norm_long, geo_type, component['long_name'])
            if hasattr(address.norm, 'unit'):
                address.norm.unit = '#' + str(address.norm.unit)
            if hasattr(address.norm_long, 'unit'):
                address.norm_long.unit = '#' + str(address.norm_long.unit)
            if hasattr(address.norm, 'street_number') and hasattr(address.norm, 'street'):
                address.norm.address = address.norm.street_number + " " + address.norm.street
            if hasattr(address.norm_long, 'street_number') and hasattr(address.norm_long, 'street'):
                address.norm_long.address = address.norm_long.street_number + " " + address.norm_long.street
            if (not hasattr(address.norm, 'city')) and hasattr(address.norm, 'administrative_area_level_3'):
                address.norm.city = address.norm.administrative_area_level_3
            if (not hasattr(address.norm_long, 'city')) and hasattr(address.norm_long, 'administrative_area_level_3'):
                address.norm_long.city = address.norm_long.administrative_area_level_3
            if (not hasattr(address.norm, 'city')) and hasattr(address.norm, 'neighborhood'):
                address.norm.city = address.norm.neighborhood
            if (not hasattr(address.norm_long, 'city')) and hasattr(address.norm_long, 'neighborhood'):
                address.norm_long.city = address.norm_long.neighborhood

class AzureMapsGeoCoder(GeoCoder):
    def config_ok(self):
        try:
            assert isinstance(self.server.daconfig['azure maps']['primary key'], str)
        except:
            logmessage("geocode: cannot geocode without a 'primary key' under 'azure maps' in the Configuration. Set 'geolocate service' in the Configuration to use a different geocoding service.")
            return False
        return True
    def initialize(self):
        from geopy.geocoders import AzureMaps
        self.geocoder = AzureMaps(self.server.daconfig['azure maps']['primary key'])
    def populate_address(self, address):
        if not 'address' in self.data.raw:
            return
        if 'freeformAddress' in self.data.raw['address']:
            address.one_line = self.data.raw['address']['freeformAddress']
            address.norm.one_line = self.data.raw['address']['freeformAddress']
            address.norm_long.one_line = self.data.raw['address']['freeformAddress']
        geo_types = {
            'municipality': 'city',
            'countrySecondarySubdivision': 'county',
            'countrySubdivision': 'state',
            'postalCode': 'postal_code',
            'extendedPostalCode': 'postal_code',
            'countryCode': 'country',
            'streetName': 'street',
            'streetNumber': 'street_number',
            'localName': 'neighborhood'
        }
        for geo_type, addr_type in geo_types.items():
            if geo_type in self.data.raw['address']:
                if (not hasattr(address, addr_type)) or getattr(address, addr_type) == '' or getattr(address, addr_type) is None:
                    setattr(address, addr_type, self.data.raw['address'][geo_type])
                setattr(address.norm, addr_type, self.data.raw['address'][geo_type])
                setattr(address.norm_long, addr_type, self.data.raw['address'][geo_type])
        if hasattr(address.norm, 'street_number') and hasattr(address.norm, 'street'):
            address.norm.address = address.norm.street_number + " " + address.norm.street
        if hasattr(address.norm_long, 'street_number') and hasattr(address.norm_long, 'street'):
            address.norm_long.address = address.norm_long.street_number + " " + address.norm_long.street
        if (not hasattr(address.norm, 'city')) and hasattr(address.norm, 'neighborhood'):
            address.norm.city = address.norm.neighborhood
        if (not hasattr(address.norm_long, 'city')) and hasattr(address.norm_long, 'neighborhood'):
            address.norm_long.city = address.norm_long.neighborhood
        if hasattr(address, 'unit'):
            address.norm.unit = address.unit
            address.norm_long.unit = address.unit
