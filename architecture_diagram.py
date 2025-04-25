import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.lines as lines

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

# Define colors
colors = {
    'main': '#3498db',  # Blue
    'service': '#2ecc71',  # Green
    'prompt': '#9b59b6',  # Purple
    'validator': '#e74c3c',  # Red
    'execution': '#f39c12',  # Orange
    'user': '#95a5a6',  # Gray
    'iac': '#1abc9c',  # Teal
    'arrow': '#34495e'  # Dark blue
}

# Create component boxes
components = {
    'user': {'pos': (1, 9), 'width': 2, 'height': 0.8, 'label': 'User', 'color': colors['user']},
    'main': {'pos': (5, 9), 'width': 2, 'height': 0.8, 'label': 'Main Controller', 'color': colors['main']},
    'router': {'pos': (5, 7.5), 'width': 2, 'height': 0.8, 'label': 'Service Router', 'color': colors['main']},
    'prompt': {'pos': (5, 6), 'width': 2, 'height': 0.8, 'label': 'Prompt Understanding', 'color': colors['prompt']},
    'ec2': {'pos': (2, 4.5), 'width': 1.8, 'height': 0.8, 'label': 'EC2 Agent', 'color': colors['service']},
    's3': {'pos': (4.1, 4.5), 'width': 1.8, 'height': 0.8, 'label': 'S3 Agent', 'color': colors['service']},
    'rds': {'pos': (6.2, 4.5), 'width': 1.8, 'height': 0.8, 'label': 'RDS Agent', 'color': colors['service']},
    'lambda': {'pos': (8.3, 4.5), 'width': 1.8, 'height': 0.8, 'label': 'Lambda Agent', 'color': colors['service']},
    'validator': {'pos': (5, 3), 'width': 2, 'height': 0.8, 'label': 'Configuration Validator', 'color': colors['validator']},
    'execution': {'pos': (5, 1.5), 'width': 2, 'height': 0.8, 'label': 'Execution Engine', 'color': colors['execution']},
    'iac': {'pos': (9, 1.5), 'width': 2, 'height': 0.8, 'label': 'IaC Generator', 'color': colors['iac']},
}

# Draw component boxes
for name, comp in components.items():
    rect = patches.Rectangle(
        comp['pos'], comp['width'], comp['height'],
        linewidth=1, edgecolor='black', facecolor=comp['color'], alpha=0.7
    )
    ax.add_patch(rect)
    ax.text(
        comp['pos'][0] + comp['width']/2, 
        comp['pos'][1] + comp['height']/2,
        comp['label'],
        ha='center', va='center', color='white', fontweight='bold'
    )

# Draw arrows
arrows = [
    # User to Main Controller
    {'start': 'user', 'end': 'main', 'label': '1. Natural Language Prompt'},
    # Main Controller to Service Router
    {'start': 'main', 'end': 'router', 'label': '2. Intent & Service'},
    # Service Router to Prompt Understanding
    {'start': 'router', 'end': 'prompt', 'label': '3. Service Context'},
    # Prompt Understanding to Service Agents
    {'start': 'prompt', 'end': 'ec2', 'label': '4a. Parameters'},
    {'start': 'prompt', 'end': 's3', 'label': '4b. Parameters'},
    {'start': 'prompt', 'end': 'rds', 'label': '4c. Parameters'},
    {'start': 'prompt', 'end': 'lambda', 'label': '4d. Parameters'},
    # Service Agents to Validator
    {'start': 'ec2', 'end': 'validator', 'label': '5a. Configuration'},
    {'start': 's3', 'end': 'validator', 'label': '5b. Configuration'},
    {'start': 'rds', 'end': 'validator', 'label': '5c. Configuration'},
    {'start': 'lambda', 'end': 'validator', 'label': '5d. Configuration'},
    # Validator to Execution Engine
    {'start': 'validator', 'end': 'execution', 'label': '6. Validated Config'},
    # Execution Engine to IaC Generator
    {'start': 'execution', 'end': 'iac', 'label': '7. Resource Definitions'},
    # Execution Engine to User
    {'start': 'execution', 'end': 'user', 'label': '8. Results', 'curved': True},
]

def get_connection_points(start_comp, end_comp):
    # Get the center points of each component
    start_x = start_comp['pos'][0] + start_comp['width'] / 2
    start_y = start_comp['pos'][1] + start_comp['height'] / 2
    end_x = end_comp['pos'][0] + end_comp['width'] / 2
    end_y = end_comp['pos'][1] + end_comp['height'] / 2
    
    # Determine which sides to connect based on relative positions
    if abs(start_x - end_x) > abs(start_y - end_y):
        # Connect horizontally
        if start_x < end_x:
            # Start component is to the left of end component
            start_point = (start_comp['pos'][0] + start_comp['width'], start_y)
            end_point = (end_comp['pos'][0], end_y)
        else:
            # Start component is to the right of end component
            start_point = (start_comp['pos'][0], start_y)
            end_point = (end_comp['pos'][0] + end_comp['width'], end_y)
    else:
        # Connect vertically
        if start_y < end_y:
            # Start component is below end component
            start_point = (start_x, start_comp['pos'][1] + start_comp['height'])
            end_point = (end_x, end_comp['pos'][1])
        else:
            # Start component is above end component
            start_point = (start_x, start_comp['pos'][1])
            end_point = (end_x, end_comp['pos'][1] + end_comp['height'])
    
    return start_point, end_point

# Draw the arrows
for arrow in arrows:
    start_comp = components[arrow['start']]
    end_comp = components[arrow['end']]
    
    if arrow.get('curved', False):
        # Create a curved path for the feedback loop
        verts = [
            (start_comp['pos'][0] + start_comp['width']/2, start_comp['pos'][1]),  # Start at bottom of execution
            (start_comp['pos'][0] + start_comp['width']/2, 0.5),  # Go down
            (0.5, 0.5),  # Go left
            (0.5, end_comp['pos'][1] + end_comp['height']/2),  # Go up
            (end_comp['pos'][0], end_comp['pos'][1] + end_comp['height']/2),  # Go right to user
        ]
        codes = [path.Path.MOVETO] + [path.Path.CURVE4] * 4
        arrow_path = path.Path(verts, codes)
        patch = patches.PathPatch(arrow_path, facecolor='none', edgecolor=colors['arrow'], linewidth=1.5, arrowstyle='->', connectionstyle='arc3,rad=0.2')
        ax.add_patch(patch)
        # Add label at the middle of the curve
        ax.text(0.7, 0.7, arrow['label'], ha='center', va='center', fontsize=8)
    else:
        start_point, end_point = get_connection_points(start_comp, end_comp)
        
        # Draw the arrow
        arrow_obj = patches.FancyArrowPatch(
            start_point, end_point,
            connectionstyle='arc3,rad=0.1', 
            arrowstyle='->', 
            linewidth=1.5, 
            color=colors['arrow']
        )
        ax.add_patch(arrow_obj)
        
        # Add label at the midpoint
        mid_x = (start_point[0] + end_point[0]) / 2
        mid_y = (start_point[1] + end_point[1]) / 2
        
        # Adjust label position to avoid overlapping with the arrow
        offset_x, offset_y = 0, 0
        if abs(start_point[0] - end_point[0]) > abs(start_point[1] - end_point[1]):
            offset_y = 0.2  # Horizontal arrow, offset vertically
        else:
            offset_x = 0.2  # Vertical arrow, offset horizontally
            
        if 'Parameters' in arrow['label']:
            # For the parameters arrows, place labels closer to the prompt understanding box
            if arrow['end'] == 'ec2':
                offset_x, offset_y = -0.4, -0.3
            elif arrow['end'] == 's3':
                offset_x, offset_y = -0.2, -0.3
            elif arrow['end'] == 'rds':
                offset_x, offset_y = 0.2, -0.3
            elif arrow['end'] == 'lambda':
                offset_x, offset_y = 0.4, -0.3
        
        if 'Configuration' in arrow['label']:
            # For the configuration arrows, place labels closer to the service agent boxes
            if arrow['start'] == 'ec2':
                offset_x, offset_y = -0.4, 0.3
            elif arrow['start'] == 's3':
                offset_x, offset_y = -0.2, 0.3
            elif arrow['start'] == 'rds':
                offset_x, offset_y = 0.2, 0.3
            elif arrow['start'] == 'lambda':
                offset_x, offset_y = 0.4, 0.3
                
        ax.text(mid_x + offset_x, mid_y + offset_y, arrow['label'], ha='center', va='center', fontsize=8)

# Add title
plt.title('AWS DevOps Agent Architecture', fontsize=16, pad=20)

# Save the diagram
plt.tight_layout()
plt.savefig('/home/ubuntu/aws_devops_agent/architecture_diagram.png', dpi=300, bbox_inches='tight')
print("Architecture diagram saved to /home/ubuntu/aws_devops_agent/architecture_diagram.png")
