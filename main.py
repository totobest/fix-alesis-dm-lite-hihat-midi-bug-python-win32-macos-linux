import time
import rtmidi
import re
import signal


midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()


def exit_condition():
    return midi_in.is_port_open() and midi_out.is_port_open()


print("Detecting Alexis DM Lite and Virtual Output devices:")
waiting = 0
while not exit_condition():
    if waiting % 10:
        print("Still waiting...")
    if not midi_in.is_port_open():
        for port_id, name in enumerate(midi_in.get_ports()):
            if not midi_in.is_port_open() and re.match('^Alesis DM Lite', name):
                midi_in.open_port(port_id)
                print("Found Input device: {}".format(name))
                break
    if not midi_out.is_port_open():
        for port_id, name in enumerate(midi_out.get_ports()):
            if re.match("FixAlesis", name, re.IGNORECASE):
                midi_out.open_port(port_id)
                print("Found Output device: {}".format(name))
                break
    if exit_condition():
        break
    time.sleep(1)
    waiting += 1

pedal = None


def on_midi_event(data, _):
    global pedal
    (stat, note, velocity), _ = data
    if stat == 185 and note == 4:
        pedal = velocity
    if stat == 153 and note == 46 and pedal > 64:
        note = 42
    # print(stat, note, velocity)
    midi_out.send_message((stat, note, velocity))


midi_in.set_callback(on_midi_event)
signal.signal(signal.SIGINT, signal.default_int_handler)

print("Ready. Press Ctrl+C to stop")
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Bye")


