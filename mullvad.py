# -*- coding: utf-8 -*-
# A basic yet complete MullVad API

import requests
import time
import subprocess


class MullvadAPI:

    API_ACCOUNT_INFO = 'https://api.mullvad.net/www/accounts/'
    API_GET_RELAYS_LIST = 'https://api.mullvad.net/public/relays/wireguard/v1/'
    API_ADD_PUBLIC_KEY = 'https://api.mullvad.net/wg/'
    API_REVOKE_PUBLIC_KEY = 'https://api.mullvad.net/www/wg-pubkeys/revoke/'
    API_CHECK_URL = 'https://am.i.mullvad.net/json'
    MULLVAD_DNS = '193.138.218.74'

    # Wg
    WIREGUARD_FOLDER = '/etc/wireguard/'
    MULLVAD_PROFILE_NAME = 'mullvad-%s.conf'

    def __init__(self, account_number: str):
        self.account_number = account_number.strip().replace(' ', '')

    # Check if device is connected to Mullvad network, including blacklist checks
    def is_vpn_connected(self):
        try:
            res = requests.get(self.API_CHECK_URL, timeout=15)
            return res.json()
        except:
            return False

    def get_relay(self, hostname):
        relays = self._list_relays_json()

        if not relays:
            return {}

        exit_location = None

        for country in relays['countries']:
            for city in country['cities']:
                for relay in city['relays']:
                    if hostname == relay['hostname']:
                        exit_location = relay
                        break

        return exit_location

    # Ie. gb11-wireguard
    # If private_key is None, it will be generated
    def generate_conf(self, hostname, private_key: int = 0):
        relay = self.get_relay(hostname)

        # Check if requested relay has been found
        if not relay:
            return False

        time.sleep(1)

        # Generate private key if hasn't been provided
        if not private_key:
            private_key = self.generate_pkey()

        # Derivate Public Key
        public_key = self._derivatePubKey(private_key)

        if not public_key:
            return False

        # Add key to MullVad profile, if needed
        # TODO check if pubkey has already been added
        allocated_address = self.add_pubkey(public_key)

        if not allocated_address:
            return False

        # Generate config
        config = '''
                [Interface]
                PrivateKey = {private_key}
                Address = {allocated_address}
                DNS = {dns}

                [Peer]
                PublicKey = {server_public_key}
                Endpoint = {server_endpoint}
                AllowedIPs = 0.0.0.0/0, ::/0'''.format(private_key=private_key,
                                                       allocated_address=allocated_address,
                                                       dns=self.MULLVAD_DNS,
                                                       server_public_key=relay['public_key'],
                                                       server_endpoint=relay['ipv4_addr_in'])

        return {'private_key': private_key,
                'public_key': public_key,
                'config': config}

    def _list_relays_json(self):
        try:
            for i in range(3):
                res = requests.get(self.API_GET_RELAYS_LIST, timeout=15).json()

                if 'code' in res and res['code'] == 'THROTTLED':
                    continue
                return res
        except:
            return None

        return False

    # Generate a private Key
    def generate_pkey(self):
        try:

            private_key = subprocess.check_output(["wg", "genkey"])
            return private_key.decode("utf-8").strip()
        except FileNotFoundError:
            print('Is wg installed and included in PATH?')
            return False

    def _derivatePubKey(self, private_key: int):
        try:
            cmd = 'echo %s | wg pubkey' % str(private_key)

            ps = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            public_key = ps.communicate()[0].decode("utf-8").strip()

            if len(str(public_key)) != 44:
                return False

            return public_key
        except FileNotFoundError:
            print('Is wg installed and included in PATH?')
            return False

    # Get account info
    def get_account_info(self):
        try:
            res = requests.get(self.API_ACCOUNT_INFO +
                               self.account_number, timeout=15)
            return res.json()
        except:
            return False

    def key_exists(self, account, public_key):
        # Check if key is actually registered
        for peer in account['account']['wg_peers']:
            if peer['key']['public'] == public_key:
                return True

        return False

    # Adding a new public key on MullVad's server.

    def add_pubkey(self, public_key: int):
        try:

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            data = {
                'account': self.account_number,
                'pubkey': public_key
            }

            res = requests.post(self.API_ADD_PUBLIC_KEY,
                                headers=headers, data=data, timeout=15)

            if res.text == 'Account does not exist':
                return False

            return res.text
        except:
            return False

    # Revoke a pubkey
    def revoke_pubkey(self, public_key: int):
        try:

            # Get authentication token
            account = self.get_account_info()

            if not account or not 'auth_token' in account:
                return False

            if not self.key_exists(account, public_key):
                print('Key cannot be revoked as it doesn\'t exist')
                return False

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Token %s' % account['auth_token']}
            data = '{"pubkey": "%s"}' % public_key
            res = requests.post(self.API_REVOKE_PUBLIC_KEY,
                                headers=headers, data=data, timeout=15)

            return res.json()
        except:
            return False
    # TODO Install a Mullvad wg profile in /etc/wireguard/
