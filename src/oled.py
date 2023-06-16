import gc
from machine import Pin, I2C
import urandom

# https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py
try:
    from ssd1306 import SSD1306_I2C
except ImportError:
    from extramodules.ssd1306 import SSD1306_I2C
gc.collect()

try:
    from writer import Writer
except ImportError:
    from extramodules.writer import Writer as Writer
try:
    import font20
except ImportError:
    import extramodules.font20_small as font20
try:
    import font10
except ImportError:
    import extramodules.font10_small as font10
gc.collect()


class Anzeige:
    # oled size
    oled_width = 64
    oled_height = 48
    # oled i2c pins
    oled_scl = 5
    oled_sda = 4
    oled_connected = False

    def __init__(self, width=oled_width, height=oled_height, scl=oled_scl, sda=oled_sda, rotate=False):
        # last printed string and box coordinates
        self.lastoutput_text = ""
        self.lastoutput_box = [0, 0, 0, 0]

        # i2c setup
        self.i2c = I2C(scl=Pin(scl), sda=Pin(sda))

        # oled setup
        try:
            self.oled = SSD1306_I2C(width, height, self.i2c)
        except OSError:
            print("oled error")
            return
        else:
            self.oled_connected = True

        gc.collect()

        # create oled font objects
        self.oled20 = Writer(self.oled, font20, verbose=False)
        self.oled10 = Writer(self.oled, font10, verbose=False)

        if rotate:
            self.oled_rotate()

        gc.collect()

    def prints(self, text, x_pos=0, y_pos=0, clear=False):
        if not self.oled_connected:
            return
        self.oled.poweron()
        if clear:
            self.oled.fill(0)
        self.oled.text(text, x_pos, y_pos)
        self.oled.show()

    def print(self, text, x_pos=0, y_pos=0, clear=False, clear_last=False, size='big'):
        if not self.oled_connected:
            return
        self.oled.poweron()
        if size == 'big':
            text_length = self.oled20.stringlen(text) - 1
            if text_length > self.oled_width:
                text_length = self.oled_width
            text_height = 20
        elif size == 'small':
            text_length = self.oled10.stringlen(text) - 1
            text_height = 10
        else:
            text_length = len(text) * 7
            text_height = 10
        if x_pos == 'center':
            posx = (self.oled_width - text_length) // 2
        elif x_pos == 'right':
            posx = max(self.oled_width - text_length - 1, 0)
        elif x_pos == 'random':
            posx = self.randrange(0, max(self.oled_width - text_length - 1, 0))
        else:
            posx = x_pos
        if y_pos == 'center':
            posy = round(self.oled_height / 2 - text_height / 2 - 1)
        elif y_pos == 'bottom':
            posy = self.oled_height - text_height - 1
        elif y_pos == 'random':
            posy = self.randrange(0, self.oled_height - text_height - 1)
        else:
            posy = y_pos

        if clear:
            self.oled.fill(0)
        elif clear_last:
            if posx > self.lastoutput_box[0] or \
                    posy > self.lastoutput_box[1] or \
                    text_length + posx < self.lastoutput_box[0] or \
                    text_height + posy < self.lastoutput_box[3]:
                self.clear_last_output()
        self.oled.fill_rect(posx, posy, text_length, text_height, 0)
        self.lastoutput_text = text
        self.lastoutput_box = [posx, posy, posx + text_length, posy + text_height]
        Writer.set_textpos(self.oled, posy, posx)
        if size == 'big':
            self.oled20.printstring(text)
        elif size == 'small':
            self.oled10.printstring(text)
        self.oled.show()

    def show_graphic(self, graphic_matrix, x, y):
        if not self.oled_connected:
            return
        for y_pos, row in enumerate(graphic_matrix):
            for x_pos, c in enumerate(row):
                self.oled.pixel(x + x_pos, y + y_pos, c)
        self.oled.show()

    def clear(self, x=0, y=0, x_width=oled_width, y_height=oled_height):
        if not self.oled_connected:
            return
        self.oled.fill_rect(x, y, x_width, y_height, 0)
        self.oled.show()

    def clear_last_output(self):
        if not self.oled_connected:
            return
        self.oled.fill_rect(self.lastoutput_box[0],
                            self.lastoutput_box[1],
                            self.lastoutput_box[2] - self.lastoutput_box[0],
                            self.lastoutput_box[3] - self.lastoutput_box[1],
                            0)
        self.oled.show()

    def poweroff(self):
        if not self.oled_connected:
            return
        self.oled.poweroff()

    def oled_rotate(self):
        if not self.oled_connected:
            return
        # turn oled upside down
        self.oled.write_cmd(0xa0)
        self.oled.write_cmd(0xc0)

    def randrange(self, minimum, maximum):
        span = maximum - minimum
        # Convert the left range into a 0-1 range (float)
        scaled = float(urandom.getrandbits(16)) / float(65535)
        # Convert the 0-1 range into a value in the right range.
        return round(minimum + (scaled * span))


if __name__ == "__main__":
    display = Anzeige()
    display.prints('start..')
