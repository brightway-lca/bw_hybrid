import subprocess
import json
from importlib.metadata import distribution
import sys

def format_size(size):
    """Convert size in bytes to a human-readable format."""
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size} bytes"

def get_dependency_tree(package_name):
    """Retrieve the dependency tree using pipdeptree."""
    cmd = ['pipdeptree', '--packages', package_name, '--json-tree']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running pipdeptree: {result.stderr}")
        sys.exit(1)
    if not result.stdout.strip():
        print(f"No dependency tree found for {package_name}. Is it installed?")
        sys.exit(1)
    try:
        tree = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from pipdeptree: {e}")
        print(f"pipdeptree output: {repr(result.stdout)}")
        sys.exit(1)
    return tree

def collect_dependencies(node, dependencies):
    """Collect unique packages and their direct dependencies."""
    package_name = node.get('key', node.get('package_name', 'unknown'))
    deps = [dep.get('key', dep.get('package_name', 'unknown')) for dep in node.get('dependencies', [])]
    dependencies[package_name] = deps
    for dep in node.get('dependencies', []):
        collect_dependencies(dep, dependencies)

def calculate_direct_sizes(unique_packages):
    """Calculate direct size of each package based on installed files."""
    direct_sizes = {}
    for package in unique_packages:
        try:
            dist = distribution(package)
            files = dist.files
            size = sum(f.locate().stat().st_size for f in files if f.locate().exists()) if files else 0
        except Exception:
            size = 0  # Package not installed or no files
        direct_sizes[package] = size
    return direct_sizes

def get_cumulative_size(package, dependencies, direct_sizes, cumulative_sizes):
    """Calculate cumulative size including all dependencies."""
    if package in cumulative_sizes:
        return cumulative_sizes[package]
    size = direct_sizes.get(package, 0)
    for dep in dependencies.get(package, []):
        size += get_cumulative_size(dep, dependencies, direct_sizes, cumulative_sizes)
    cumulative_sizes[package] = size
    return size

def print_tree(node, dependencies, direct_sizes, cumulative_sizes, indent=0):
    """Print the dependency tree with sizes."""
    package_name = node.get('key', node.get('package_name', 'unknown'))
    direct_size = direct_sizes.get(package_name, 0)
    cumulative_size = get_cumulative_size(package_name, dependencies, direct_sizes, cumulative_sizes)
    size_str = f"{package_name} (direct: {format_size(direct_size)}, cumulative: {format_size(cumulative_size)})"
    print(' ' * indent + size_str)
    for dep in node.get('dependencies', []):
        print_tree(dep, dependencies, direct_sizes, cumulative_sizes, indent + 4)

def main():
    """Process the package and display its dependency tree with sizes, followed by a sorted list of packages by size."""
    if len(sys.argv) != 2:
        print("Usage: python size.py <package_name>")
        sys.exit(1)
    
    package_name = sys.argv[1]
    tree = get_dependency_tree(package_name)
    root = tree[0]  # Root package
    
    # Collect dependencies
    dependencies = {}
    collect_dependencies(root, dependencies)
    
    # Calculate direct sizes for all unique packages
    unique_packages = set(dependencies.keys())
    direct_sizes = calculate_direct_sizes(unique_packages)
    
    # Sort packages by direct size in descending order
    sorted_packages = sorted(direct_sizes.items(), key=lambda x: x[1], reverse=True)
    
    # Print the dependency tree
    cumulative_sizes = {}
    print_tree(root, dependencies, direct_sizes, cumulative_sizes)
    
    # Print the sorted list of packages by direct size
    print("\nPackages by file size:")
    for package, size in sorted_packages:
        print(f"- {package}: {format_size(size)}")

if __name__ == "__main__":
    main()