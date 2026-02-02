# Implemented for manual control only at this time:
# Objectives:
# -Create vehicle
# -Add proper parts (Camera, Controller(TeensyRC or WebController), Drivetrain, Add Data Storage Tub)
import donkeycar as dk
from donkeycar.parts.tub_v2 import TubWriter
from donkeycar.parts.datastore import TubHandler
from donkeycar.parts.controller import LocalWebController, WebFpv
from donkeycar.parts.Teensy_RC import TeensyRC
from donkeycar.parts.actuator import ArduinoFirmata, ArdPWMSteering, ArdPWMThrottle
from donkeycar.parts.transform import Lambda
from donkeycar.parts.pipe import Pipe
from docopt import docopt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def drive(cfg, use_joystick, camera_type = 'single', meta=[]):
    # Initialize logging before anything else to allow console logging
    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)
    
    # Initialize car
    V = dk.vehicle.Vehicle()

    # Add Camera:
    add_camera(V, cfg, camera_type)

    # Add controller
    # Recording default
    V.add(lambda: False, outputs=['recording'])
    if use_joystick:
        ctr = TeensyRC()
        V.add(ctr,outputs=['user/steering', 'user/throttle'], threaded=True)
    else:
        ctr = ctr = add_user_controller(V, cfg)
        # V.add handled inside add_user_controller method

    # convert 'user/steering' to 'user/angle' to be backward compatible with deep learning data
    V.add(Pipe(), inputs=['user/steering'], outputs=['user/angle'])
    
    # Setup drivetrain
    add_drivetrain(V, cfg)

    # For data storage of collected image/angle/throttle bundles
    # Create data storage part
    tub_path = TubHandler(path=cfg.DATA_PATH).create_tub_path() if \
        cfg.AUTO_CREATE_NEW_TUB else cfg.DATA_PATH
    meta += getattr(cfg, 'METADATA', [])

    inputs = ['cam/image_array', 'user/angle', 'user/throttle']
    types = ['image_array', 'float', 'float']
    tub_writer = TubWriter(tub_path, inputs=inputs, types=types, metadata=meta)
    V.add(tub_writer, inputs=inputs, outputs=["tub/num_records"], run_condition='recording')

    # Run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ, max_loop_count=cfg.MAX_LOOPS)
########################################################################
#                             METHODS                                  #
########################################################################
def add_user_controller(V, cfg, use_joystick, input_image='ui/image_array'):
    """
    Add the web controller and any other
    configured user input controller.
    :param V: the vehicle pipeline.
              On output this will be modified.
    :param cfg: the configuration (from myconfig.py)
    :return: the controller
    """
    #
    # This web controller will create a web server that is capable
    # of managing steering, throttle, and modes, and more.
    #
    ctr = LocalWebController(port=cfg.WEB_CONTROL_PORT, mode=cfg.WEB_INIT_MODE)
    V.add(ctr,
        inputs=[input_image, 'tub/num_records', 'user/mode', 'recording'],
        outputs=['user/steering', 'user/throttle', 'user/mode', 'recording', 'web/buttons'],
        threaded=True)
    return ctr

def get_camera(cfg):
    """
    Get the configured camera part
    """
    cam = None
    if not cfg.DONKEY_GYM:
        cfg.CAMERA_TYPE == "CSIC"
        from donkeycar.parts.camera import CSICamera
        cam = CSICamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH,
                        capture_width=cfg.IMAGE_W, capture_height=cfg.IMAGE_H,
                        framerate=cfg.CAMERA_FRAMERATE, gstreamer_flip=cfg.CSIC_CAM_GSTREAMER_FLIP_PARM)
    return cam


def add_camera(V, cfg, camera_type):
    """
    Add the configured camera to the vehicle pipeline.

    :param V: the vehicle pipeline.
              On output this will be modified.
    :param cfg: the configuration (from myconfig.py)
    """
    logger.info("cfg.CAMERA_TYPE %s"%cfg.CAMERA_TYPE)
    inputs = []
    outputs = ['cam/image_array']
    threaded = True
    cam = get_camera(cfg)
    if cam:
        V.add(cam, inputs=inputs, outputs=outputs, threaded=threaded)

def add_drivetrain(V, cfg):
    if cfg.DRIVE_TRAIN_TYPE == "ARDUINO":
        arduino_controller = ArduinoFirmata(servo_pin=cfg.STEERING_ARDUINO_PIN, esc_pin=cfg.THROTTLE_ARDUINO_PIN)
        steering = ArdPWMSteering(controller=arduino_controller,
                                  left_pulse=cfg.STEERING_ARDUINO_LEFT_PWM,
                                  right_pulse=cfg.STEERING_ARDUINO_RIGHT_PWM)

        throttle = ArdPWMThrottle(controller=arduino_controller,
                                  max_pulse=cfg.THROTTLE_ARDUINO_FORWARD_PWM,
                                  zero_pulse=cfg.THROTTLE_ARDUINO_STOPPED_PWM,
                                  min_pulse=cfg.THROTTLE_ARDUINO_REVERSE_PWM)
        V.add(steering, inputs=['user/angle'])
        V.add(throttle, inputs=['user/throttle'])
########################################################################
#                       START THE DRIVE LOOP                           #
########################################################################
if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config(myconfig=args['--myconfig'])

    if args['drive']:
        model_type = args['--type']
        camera_type = args['--camera']
        drive(cfg, model_path=args['--model'], use_joystick=args['--js'],
              model_type=model_type, camera_type=camera_type,
              meta=args['--meta'])
    elif args['train']:
        print('Use python train.py instead.\n')