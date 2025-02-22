#!/usr/bin/python3

# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua

# import application libraries
from lib.NavigationControls import NavigationControls

# import python libraries
import math
import time

# constant size of the window on the monitor in meters
SCREEN_SIZE = avango.gua.Vec2(0.45, 0.25)

# appends a camera node, screen node, and navigation capabilities to the scenegraph
class DesktopViewingSetup:

    def __init__(self, scenegraph):
        self.scenegraph = scenegraph

        # navigation node
        self.navigation_node = avango.gua.nodes.TransformNode(
            Name='navigation_node')
        self.navigation_controls = NavigationControls()
        self.navigation_controls.set_scenegraph(self.scenegraph)
        self.navigation_node.Transform.connect_from(
            self.navigation_controls.sf_output_matrix)
        self.scenegraph.Root.value.Children.value.append(self.navigation_node)

        # avatar
        self.loader = avango.gua.nodes.TriMeshLoader()
        self.avatar = self.loader.create_geometry_from_file('avatar',
                                                            'data/objects/figure.obj',
                                                            avango.gua.LoaderFlags.LOAD_MATERIALS)

        for child in self.avatar.Children.value:
            child.Material.value.set_uniform("Roughness", 0.6)
        self.navigation_node.Children.value.append(self.avatar)

        # 
        self.rotate_camera = avango.gua.nodes.TransformNode(Name='rotate_camera')
        self.rotate_camera.Transform.value = avango.gua.make_trans_mat(0,0,0)
        self.navigation_node.Children.value.append(self.rotate_camera)
        self.rotate_camera.Transform.connect_from(self.navigation_controls.sf_rotation_output_matrix)

        self.follow_figure = avango.gua.nodes.TransformNode(Name='follow_figure')
        self.follow_figure.Transform.value = avango.gua.make_trans_mat(0,0,25)
        self.rotate_camera.Children.value.append(self.follow_figure)

        # screen node
        self.screen_dimensions = SCREEN_SIZE
        self.screen_node = avango.gua.nodes.ScreenNode(Name='screen_node')
        self.screen_node.Width.value = self.screen_dimensions.x
        self.screen_node.Height.value = self.screen_dimensions.y
        self.screen_node.Transform.value = avango.gua.make_trans_mat(
            0.0, 0.0, -0.6)
        self.follow_figure.Children.value.append(self.screen_node)

        # camera node (head)
        self.camera_node = avango.gua.nodes.CameraNode(Name='camera_node')
        self.camera_node.SceneGraph.value = self.scenegraph.Name.value
        self.camera_node.LeftScreenPath.value = self.screen_node.Path.value
        self.camera_node.BlackList.value = ['invisible']
        self.follow_figure.Children.value.append(self.camera_node)

    # registers a window created in the class Renderer with the camera node
    def register_window(self, window):
        self.camera_node.OutputWindowName.value = window.Title.value
        self.camera_node.Resolution.value = window.Size.value
        avango.gua.register_window(window.Title.value, window)

    # registers a pipeline description in the class Renderer with the camera node
    def register_pipeline_description(self, pipeline_description):
        self.camera_node.PipelineDescription.value = pipeline_description