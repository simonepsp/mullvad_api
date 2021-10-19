# Mullvad API
A fully-fledged Mullvad API for Python.

This is a 2-hours project so expect bugs, random code and *ghosts* waking you up at night [^1].

Most methods just rely on standard Mullvad APIs (I used this bash script as inspiration https://mullvad.net/media/files/mullvad-wg.sh).


This should cover generic use-cases such as: config generation, key uploading, key revoking, account info, relays list, etc etc

Only requirement is Python 3.X and wireguard for key generation (https://www.wireguard.com/install/).


Let me know if something doesn't work for you. 
PRs are very welcome.

# Init
```mullvad = MullvadAPI(ACCOUNT_NUMBER)```

# List countries relays
```

relays = mullvad._list_relays_json()


for country in relays['countries']:
    print('\n= %s [ %s ] =' % (country['name'], country['code']))

    for city in country['cities']:
        print('%s [ %s ]' % (city['name'], city['code']))
        for relay in city['relays']:
            print('\t----> %s [ %s ]' % (relay['hostname'], relay['ipv4_addr_in']))

print('There are %d countries listed on MullVad' % len(relays['countries']))

```

# Am I connected to Mullvad network?
```mullvad.is_vpn_connected()```

# Get a specific exit location (by relay hostname)
```mullvad.get_relay('us58-wireguard')```

# A) Generate a private key
```mullvad.generate_pkey()```

# B) Or derivate a public key (from a private key)
```mullvad._derivatePubKey(PRIVATE_KEY)```

# Upload your new key to MullVad
```mullvad.add_pubkey(PUBLIC_KEY)```

# Revoke a public key you previously uploaded
- Mullvad API will get an authorization token for you, using your account number and then revoke the relevant key
```
mullvad.revoke_pubkey(PUBLIC_KEY)
```

# Also, you can do that with a one-liner
```res = mullvad.generate_conf(hostname='us58-wireguard')```

# Or by providing a private key 
```
res = mullvad.generate_conf(hostname='us58-wireguard', private_key = private_key)
print(res['config'])
```

<img width="674" alt="CleanShot 2021-10-19 at 14 28 53@2x" src="https://user-images.githubusercontent.com/11884948/137900667-1388f71a-ed2b-442d-9c08-ec6fe6d9acb5.png">

[^1]: Yes, ghosts are real
