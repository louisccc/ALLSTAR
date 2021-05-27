import allstar
import sys
import os
from io import BytesIO
from elftools.elf.elffile import ELFFile

def contains_debug(elf):
    return bool(elf.get_section_by_name('.debug_info') or
            elf.get_section_by_name('.zdebug_info'))

def num_dwarf_cu(dwarfinfo):
    num_cu = 0
    for compile_unit in dwarfinfo.iter_CUs():
        num_cu += 1
    return num_cu

def valid_debug_elf(elf):
    if not contains_debug(elf):
        return False
        
    dwarfinfo=elf.get_dwarf_info()    
    if not (1 <= num_dwarf_cu(dwarfinfo)):
        return False

    return True

def fetch_debug_binaries(repo, dst_dir):
    allstar_packages = repo.package_list()
    
    rsize = len(allstar_packages)
    index = 0
    fetched_pkg = 0
    fetched_bin = 0
    for pkg in allstar_packages:

        pkg = pkg.strip()
        index += 1
        fetched_pkg += 1
        
        try:
            print("[%d of %d] %s..." % (index,rsize,pkg))

            pkg_path = os.path.join(dst_dir, pkg)
            os.mkdir(pkg_path)

            for b in repo.package_binaries(pkg):
                elf = ELFFile(BytesIO(b['content']))
                if valid_debug_elf(elf):

                    fetched_bin += 1
                    binary_name = pkg_path + '/' + b['name']
                    with open(binary_name, 'wb') as f:
                        f.write(b['content'])

            if not os.listdir(pkg_path):
                fetched_pkg -= 1
                os.rmdir(pkg_path)

        except:

            continue

    return (fetched_bin, fetched_pkg)

def fetch_all_binaries(repo, dst_dir):
    allstar_packages = repo.package_list()
    
    rsize = len(allstar_packages)
    index = 0
    fetched_pkg = 0
    fetched_bin = 0
    for pkg in allstar_packages:

        pkg = pkg.strip()
        index += 1
        fetched_pkg += 1
        
        try:
            print("[%d of %d] %s..." % (index,rsize,pkg))

            pkg_path = os.path.join(dst_dir, pkg)
            os.mkdir(pkg_path)

            for b in repo.package_binaries(pkg):
                fetched_bin += 1
                binary_name = pkg_path + '/' + b['name']
                with open(binary_name, 'wb') as f:
                    f.write(b['content'])

            if not os.listdir(pkg_path):
                fetched_pkg -= 1
                os.rmdir(pkg_path)

        except:

            continue

    return (fetched_bin, fetched_pkg)
    

if __name__ == '__main__':
    try:
        dst_dir = sys.argv[1]
        dst_dir = os.path.abspath(dst_dir)

        if not os.path.isdir(dst_dir):
            raise ValueError("Passed directory invalid")
        print("\nSaving ALLSTAR amd64 binaries to " + dst_dir)

    except:
        print("\nEnter valid directory as an argument\n")
        quit()

    repo = allstar.AllstarRepo("amd64")
    (num_bins, num_pkg) = fetch_debug_binaries(repo, dst_dir)

    print("\nDownloaded %d binaires from %d packages.", (num_bins, num_pkg))