import json
import sys
import texttable
import pandas as pd
from datetime import datetime

def report_1(data):
    table = texttable.Texttable()
    table.set_cols_width([16,16,18,26,9,11,14,7,11,21,26,6,6,21])
    titles = ["Domain Name","Scan Time","IPv4","IPv6","Server","Insecure HTTP","Redirect to HTTPS","HSTS","TLS","Root CA","RDNS Names","Minimum RTT","Maximum RTT","Locations"]
    table.set_cols_align(['c'] * len(titles))
    table.header(titles)
    for index, row in data.iterrows():
        res = [index, datetime.utcfromtimestamp(row['scan_time'])]
        fields = ['ipv4_addresses','ipv6_addresses','http_server','insecure_http','redirect_to_https','hsts','tls_versions','root_ca','rdns_names','rtt_min','rtt_max','geo_locations_list']
        for field in fields:
            field_data = row[field]
            if isinstance(field_data, list):
                tmp = '\n'.join(field_data)
                res.append(tmp)
            elif isinstance(field_data, bool):
                if row[field]:
                    res.append('YES')
                else:
                    res.append('NO')
            else:
                res.append(row[field])
        table.add_row(res)
    return table


def report_2(data):
    table = texttable.Texttable()
    titles = ["Domain Name","Minimum RTT","Maximum RTT"]
    table.set_cols_align(['c'] * 3)
    table.header(titles)
    sorted_data = data.sort_values(by=['rtt_min'])
    for index, row in sorted_data.iterrows():
        table.add_row([index, row['rtt_min'], row['rtt_max']])

    return table

def report_3(data):
    
    table = texttable.Texttable()
    df = data.groupby(['root_ca']).size().reset_index(name='count')
    df = df.sort_values(by=['count'], ascending=False)
    titles = ["Root Certificate Authority","Count"]
    table.set_cols_align(['c'] * 2)
    table.header(titles)
    for _, row in df.iterrows():
        table.add_row([row['root_ca'], row['count']])
    return table

def report_4(data):

    table = texttable.Texttable()
    df = data.groupby(['http_server']).size().reset_index(name='count')
    df = df.sort_values(by=['count'], ascending=False)
    titles = ["Web Server","Count"]
    table.set_cols_align(['c'] * 2)
    table.header(titles)
    for _, row in df.iterrows():
        table.add_row([row['http_server'], row['count']])
    return table


def report_5(data):
    
    table = texttable.Texttable()
    df = data
    df['TLSv1.0'] = df['tls_versions'].str.contains('TLSv1.0', na=False, regex=False)
    df['TLSv1.1'] = df['tls_versions'].str.contains('TLSv1.1', na=False, regex=False)
    df['TLSv1.2'] = df['tls_versions'].str.contains('TLSv1.2', na=False, regex=False)
    df['TLSv1.3'] = df['tls_versions'].str.contains('TLSv1.3', na=False, regex=False)
    df['ipv6_enabled'] = df['ipv6_addresses']
    for i in range(len(df['ipv6_addresses'])):
        if(len(df['ipv6_addresses'][i]) == 0):
            df['ipv6_enabled'][i] = 0.0
        else:
            df['ipv6_enabled'][i] = 1.0
    
    # df.loc[df['ipv6_addresses'].str.len() != 0, 'ipv6_enabled'] = 1.0
    filters = ['TLSv1.0', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3', 'SSLv2', 'SSLv3', 'insecure_http', 'redirect_to_https','hsts', 'ipv6_enabled']
    res = []
    for index in filters:
        if index == "SSLv2" or index == "SSLv3":
            res.append("0.0%")
        else:
            _ = df.groupby([index]).size().reset_index(name='count')
            _ = _.sort_values(by=[index], ascending=False)
            perc = int(df[index].sum() / len(df) * 100)
            res.append(str(perc) + " %")
    titles = ['TLSv1.0', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3', 'SSLv2', 'SSLv3', 'Insecure HTTP', 'Redirect to HTTPS','HTTP Strict Transport Security', 'IPv6 Enabled']
    table.set_cols_width([8, 8, 8, 8, 8, 8, 11, 11, 11, 11])
    table.set_cols_align(['c'] * 10)
    table.header(titles)
    table.add_row(res)

    return table



def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)

    df = pd.DataFrame(data).transpose()

    for i in range(len(df['rtt_range'])):
        if(not isinstance(df['rtt_range'][i],list)):
            df['rtt_range'][i] = [None, None]

    df[['rtt_min', 'rtt_max']] = df.rtt_range.to_list()
    part_1_table = report_1(df)
    part_2_table = report_2(df)
    part_3_table = report_3(df)
    part_4_table = report_4(df)
    part_5_table = report_5(df)
    write_to_file(content=part_1_table.draw() + '\n' + part_2_table.draw() + '\n' + part_3_table.draw() + '\n' + part_4_table.draw() + '\n' + part_5_table.draw(),file_name=sys.argv[2])

def write_to_file(content: str, file_name: str):
    with open(file_name, "w") as f:
        f.write(content)


if __name__ == '__main__':
    main()