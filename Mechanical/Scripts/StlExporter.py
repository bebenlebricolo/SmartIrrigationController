"""
FreeCAD STL Exporter Script

This script exports selected Part bodies or Part containers to STL files
in the Exports folder. It can handle:
- Regular Part Bodies (PartDesign::Body, Part::Feature)
- Part containers that contain multiple bodies

Usage:
1. Select objects in FreeCAD that you want to export
2. Run this script (Macros -> StlExporter or via Python console)
3. Files will be created in the Exports folder with automatic names

To manually specify object-to-filename mapping, modify the get_output_filename() function.
"""

import FreeCAD
import FreeCADGui
import os
import re


def get_exports_folder():
    """Get or create the Exports folder path relative to the active document."""
    doc = FreeCAD.ActiveDocument
    if doc:
        doc_path = os.path.dirname(doc.FileName)
    else:
        doc_path = os.getcwd()
    
    exports_path = os.path.join(doc_path, "Exports")
    if not os.path.exists(exports_path):
        os.makedirs(exports_path)
    return exports_path


def sanitize_filename(name):
    """Sanitize a name to be used as a filename (remove special characters)."""
    # Remove invalid characters for filenames
    sanitized = re.sub(r'[\\/*?:"<>|]', '', name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized


def get_output_filename(obj):
    """
    Generate output filename for an object.
    
    To customize the mapping, modify this function or add a mapping dictionary.
    For example:
        _filename_map = {
            'MyBody': 'custom_name',
            'AnotherBody': 'another_name'
        }
    
    Args:
        obj: FreeCAD object to export
    
    Returns:
        str: Output filename without extension
    """
    # Default: use the object's label or name
    name = obj.Label if obj.Label else obj.Name
    
    # Add your custom object-to-filename mapping here
    # _filename_map = {
    #     'Body': 'main_body',
    #     'Gear': 'gear_part'
    # }
    # if name in _filename_map:
    #     return _filename_map[name]
    
    return sanitize_filename(name)


def is_body(obj):
    """Check if an object is a Part or PartDesign Body."""
    if hasattr(obj, 'Proxy') and obj.Proxy:
        proxy_type = obj.Proxy.__class__.__name__
        if 'Body' in proxy_type or 'Part' in proxy_type:
            return True
    
    # Check for PartDesign::Body
    if hasattr(obj, 'TypeId'):
        if 'PartDesign::Body' in obj.TypeId:
            return True
        if 'Part::Feature' in obj.TypeId:
            return True
    
    # Check for common body indicators
    if hasattr(obj, 'Tip') and 'Body' in obj.Tip:
        return True
    
    # Check if it has Shape property (is a solid)
    if hasattr(obj, 'Shape') and obj.Shape:
        return True
    
    return False


def is_part_container(obj):
    """Check if an object is a Part container that can contain bodies."""
    if hasattr(obj, 'Group'):
        return True
    if hasattr(obj, 'getObjects'):
        return True
    if hasattr(obj, 'getObjectsByLabel'):
        return True
    if hasattr(obj, 'TypeId') and 'Part' in obj.TypeId:
        # Some Part containers have TypeId containing 'Part'
        return True
    return False


def get_bodies_from_container(obj):
    """Extract all bodies from a Part container."""
    bodies = []
    
    # Try different methods to get children
    if hasattr(obj, 'getObjects'):
        children = obj.getObjects()
    elif hasattr(obj, 'Group'):
        children = obj.Group
    elif hasattr(obj, 'getObjectsByLabel'):
        # Get all objects in container
        labels = obj.getObjectNames() if hasattr(obj, 'getObjectNames') else []
        children = [obj.getObject(label) for label in labels]
    else:
        children = []
    
    for child in children:
        if is_body(child):
            bodies.append(child)
        elif is_part_container(child):
            # Recursively get bodies from nested containers
            bodies.extend(get_bodies_from_container(child))
    
    return bodies


def export_body_to_stl(body, filepath):
    """Export a single body to STL file."""
    try:
        # Method 1: Using Mesh module (most reliable for STL)
        if hasattr(body, 'Shape') and body.Shape:
            import Mesh
            mesh = Mesh.Mesh()
            # Create mesh from shape
            mesh.addFacet(body.Shape.tessellate(0.1))  # 0.1 is the deflection
            mesh.write(filepath)
            print(f"  Exported: {filepath}")
            return True
        else:
            print(f"  Warning: Body {body.Name} has no Shape property")
            return False
    except Exception as e:
        print(f"  Error exporting {body.Name}: {e}")
        return False


def export_to_stl():
    """Main export function - exports selected objects to STL."""
    doc = FreeCAD.ActiveDocument
    if not doc:
        print("No active document. Please open a document first.")
        return
    
    selection = FreeCADGui.Selection.getSelection()
    
    if not selection:
        print("No objects selected. Please select objects to export.")
        return
    
    exports_folder = get_exports_folder()
    print(f"Exporting to: {exports_folder}")
    
    exported_count = 0
    
    for obj in selection:
        filename_base = get_output_filename(obj)
        
        if is_body(obj):
            # Export single body
            filepath = os.path.join(exports_folder, f"{filename_base}.stl")
            if export_body_to_stl(obj, filepath):
                exported_count += 1
        elif is_part_container(obj):
            # Export all bodies from container
            bodies = get_bodies_from_container(obj)
            if bodies:
                for body in bodies:
                    body_filename = get_output_filename(body)
                    filepath = os.path.join(exports_folder, f"{filename_base}_{body_filename}.stl")
                    if export_body_to_stl(body, filepath):
                        exported_count += 1
            else:
                # Try to export the container itself if it has a shape
                filepath = os.path.join(exports_folder, f"{filename_base}.stl")
                if export_body_to_stl(obj, filepath):
                    exported_count += 1
        else:
            # Try to export anyway if it has a Shape
            if hasattr(obj, 'Shape') and obj.Shape:
                filepath = os.path.join(exports_folder, f"{filename_base}.stl")
                if export_body_to_stl(obj, filepath):
                    exported_count += 1
            else:
                print(f"  Skipping {obj.Name}: not a body or container with shape")
    
    print(f"\nExported {exported_count} objects to STL files in {exports_folder}")


def export_all_bodies_to_stl():
    """Export all bodies in the active document to STL files."""
    doc = FreeCAD.ActiveDocument
    if not doc:
        print("No active document. Please open a document first.")
        return
    
    exports_folder = get_exports_folder()
    print(f"Exporting all bodies to: {exports_folder}")
    
    exported_count = 0
    
    # Find all bodies in the document
    all_objects = doc.Objects
    for obj in all_objects:
        if is_body(obj):
            filename_base = get_output_filename(obj)
            filepath = os.path.join(exports_folder, f"{filename_base}.stl")
            if export_body_to_stl(obj, filepath):
                exported_count += 1
        elif is_part_container(obj):
            bodies = get_bodies_from_container(obj)
            for body in bodies:
                filename_base = get_output_filename(body)
                # Use container name as prefix
                container_name = sanitize_filename(obj.Label if obj.Label else obj.Name)
                filepath = os.path.join(exports_folder, f"{container_name}_{filename_base}.stl")
                if export_body_to_stl(body, filepath):
                    exported_count += 1
    
    print(f"\nExported {exported_count} bodies to STL files in {exports_folder}")


# Check if running in FreeCAD
if 'FreeCAD' in globals() and FreeCAD.__version__:
    # Running in FreeCAD - export selected objects
    export_to_stl()
else:
    # Running standalone - just define functions
    print("FreeCAD STL Exporter loaded. Run export_to_stl() or export_all_bodies_to_stl() in FreeCAD.")
