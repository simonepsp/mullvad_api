# -*- coding: utf-8 -*-
from mullvad import MullvadAPI

# --->
ACCOUNT_NUMBER = '###################'

mullvad = MullvadAPI(ACCOUNT_NUMBER)

# --- List countries
relays = mullvad._list_relays_json()
countries = relays['countries']

# for country in countries:
#     print('\n= %s [ %s ] =' % (country['name'], country['code']))

#     for city in country['cities']:
#         print('%s [ %s ]' % (city['name'], city['code']))
#         for relay in city['relays']:
#             print('\t----> %s [ %s ]' % (relay['hostname'], relay['ipv4_addr_in']))

print('There are %d countries listed on MullVad' % len(relays))

# -- Get a specific exit location (by hostname)
# print(mullvad.get_relay('us58-wireguard'))


# --- A) Create private and public key
# private_key = mullvad.generate_pkey()

# print('Private Key: %s' % str(private_key))

# public_key = mullvad._derivatePubKey(private_key)

# print('Public Key: %s' % str(public_key))

# --- B) Or just upload an existing private key to Mullvad
# print(mullvad.add_pubkey(public_key))
private_key = 'uO/q4VmwVy62UJpFdcup/w+pjYPiNa603xshTsjr10s='

# ---- And let MullvadAPI generate a wireguard configuration, given a hostname
res = mullvad.generate_conf(hostname='us58-wireguard') # , private_key = private_key

print(res)

# Finally, revoke the key from MullVad
public_key = mullvad._derivatePubKey(private_key)
print(mullvad.revoke_pubkey(res['public_key']))