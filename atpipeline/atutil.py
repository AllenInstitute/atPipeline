import os
import pathlib
import argparse
import re
import os
import json

def main():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help='sub-command help')
    subparsers.required = True

    # create the parser for the "rename" command
    parser_rename = subparsers.add_parser('rename', help='Rename a channel')
    parser_rename.add_argument('oldname', help='Old name (e.g. DAPI1)')
    parser_rename.add_argument('newname', help='New name (e.g. DAPI_1)')
    parser_rename.add_argument('--data', help="Path to data", required=True)
    parser_rename.add_argument('--dryrun', help="Dry run (don't touch data)", default=False, action="store_true")

    args = parser.parse_args()

    if args.command == "rename":
        rename(args.oldname, args.newname, args.data, args.dryrun)



def update_metadata(oldfile, newfile, oldchannel, newchannel, dryrun=False, json_format=False):
    """Update references from oldchannel to newchannel.
       Newfile may be "None" to update inplace.
    """

    data = oldfile.read_text()
    if json_format:
        json_data = json.loads(data)
        if oldfile.name == "session_metadata.json":
            for i in range(len(json_data["all_channels"])):
                if json_data["all_channels"][i]["channel"] == oldchannel:
                    json_data["all_channels"][i]["channel"] = newchannel
        else:
            json_data["channelname"] = newchannel
        data = json.dumps(json_data)
    else:
        data = re.sub(r'^%s\t' % oldchannel, "%s\t" % newchannel, data, count=1, flags=re.MULTILINE)

    if not dryrun:
        if newfile:
            newfile.write_text(data)
            oldfile.unlink()
        else:
            oldfile.write_text(data)
    else:
        print("Dry run: not updating %s to %s" % (oldfile, newfile))


def rename(oldname, newname, data, dryrun=False):
    datapath = pathlib.Path(data)
    for child in datapath.rglob("*"):
        # raw/data/Ribbon0004/session01/session_metadata.txt
        if child.name == "session_metadata.txt":
            # Edit file to replace channel name at start of line!
            print("Updating %s" % child)
            update_metadata(child, None, oldname, newname, dryrun)
        elif child.name == "session_metadata.json":
            print("Updating %s" % child)
            update_metadata(child, None, oldname, newname, dryrun, json_format=True)
        else:
            # raw/data/Ribbon0004/session01/PSD95/PSD95_S0000_F0001_Z00_metadata.txt
            # raw/data/Ribbon0004/session01/PSD95/PSD95_S0001_F0006_Z00.tif
            parts = child.parts
            # Try to match file...
            m = re.match(r'(?P<channel>.*)(?P<rest>_S\d{4}_F\d{4}_Z\d{2}(.tif|_metadata.txt|_metadata.json))', parts[-1])
            if m:
                channel = m.group('channel')
                if channel == oldname:
                    newdir = pathlib.Path(child.parents[1], newname)
                    newfile = pathlib.Path(newdir, newname + m.group('rest'))
                    # print(newdir, newfile)
                    newdir.mkdir(exist_ok=True)

                    # Found a file to move
                    if parts[-1].endswith(".tif"):
                        # Image data, move it!
                        if not dryrun:
                            child.rename(newfile)
                        else:
                            print("Dry run: not moving %s to %s" % (child, newfile))
                    elif parts[-1].endswith("_metadata.txt"):
                        update_metadata(child, newfile, oldname, newname, dryrun)
                    elif parts[-1].endswith("_metadata.json"):
                        update_metadata(child, newfile, oldname, newname, dryrun, json_format=True)
                else:
                    print("Skipping data from channel %s" % channel)
            else:
                print("Skipping file %s" % child)

if __name__ == '__main__':
    main()
