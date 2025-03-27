import nmea
import math

def print_optional_double(label, value, unit=""):
    if not math.isnan(value):
        print("- {}: {:.1f} {}".format(label, value, unit))
    else:
        print("- {}: N/A".format(label))

def print_optional_coord(label, coord, dir_str):
    if not math.isnan(coord):
        deg = math.floor(coord)
        minute = (coord - deg) * 60.0
        print("- {}: {:.0f}°{:.4f}' {}".format(label, deg, minute, dir_str))
    else:
        print("- {}: N/A".format(label))

def print_optional_int(label, value, unit=""):
    if value != -1:
        print("- {}: {} {}".format(label, value, unit))
    else:
        print("- {}: N/A".format(label))

def print_gga_data(gga):
    print("GGA Data:")
    print_optional_coord("Latitude", gga.get("latitude"), "N")
    print_optional_coord("Longitude", gga.get("longitude"), "W")
    print_optional_int("GPS Quality", gga.get("fix_type"), "(GPS fix)")
    print_optional_int("Number of Satellites", gga.get("fix_satellites"))
    print_optional_double("Horizontal Dilution of Precision", gga.get("hdop"))
    print_optional_double("Altitude", gga.get("altitude"), "Meters")
    print_optional_double("Height of Geoid above WGS84 Ellipsoid", gga.get("geoid_separation"), "Meters")

def main():
    # Get a message from the Rust/C library
    msg = nmea.hello()
    print("Message from Rust: {}".format(msg))
    
    size = nmea.nmea_size()
    print("Size of NMEA: {}".format(size))
    
    alt = nmea.nmea_gga_altitude("$GPGGA,092750.000,5321.6802,N,00630.3372,W,1,8,1.03,61.7,M,55.2,M,,*76")
    print("NMEA altitude: {:.2f}".format(alt))
    
    # Parse the GGA sentence and print the data.
    gga = nmea.parse_nmea_gga("$GPGGA,092750.000,5321.6802,N,00630.3372,W,1,8,1.03,61.7,M,55.2,M,,*76")
    print_gga_data(gga)

main()

