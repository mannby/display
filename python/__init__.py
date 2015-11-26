
import base64
import json
import numpy
import urllib2
import uuid

from . import png

__all__ = ['URL', 'image', 'images', 'plot']

URL = 'http://localhost:8000/events'


def uid():
  return 'pane_%s' % uuid.uuid4()


def send(**command):
  command = json.dumps(command)
  req = urllib2.Request(URL)
  req.add_header('Content-Type', 'application/text')
  req.data = command.encode('ascii')
  try:
    resp = urllib2.urlopen(req)
    return resp != None
  except:
    raise
    return False


def normalize(img, opts):
  minval = opts.get('min')
  if minval is None:
    minval = numpy.amin(img)
  maxval = opts.get('max')
  if maxval is None:
    maxval = numpy.amax(img)

  return numpy.uint8((img - minval) * (255/(maxval - minval)))


def to_rgb(img):
  nchannels = img.shape[2] if img.ndim == 3 else 1
  if nchannels == 3:
    return img
  if nchannels == 1:
    return img[:, :, numpy.newaxis].repeat(3, axis=2)
  raise ValueError('Image must be RGB or gray-scale')


def image(img, **opts):
  assert img.ndim == 2 or img.ndim == 3
  win = opts.get('win') or uid()

  if isinstance(img, list):
    return images(img, opts)
  # TODO: if img is a 3d tensor, then unstack it into a list of images

  img = to_rgb(normalize(img, opts))
  pngbytes = png.encode(img.tostring(), img.shape[1], img.shape[0])
  imgdata = 'data:image/png;base64,' + base64.b64encode(pngbytes).decode('ascii')

  send(command='image', id=win, src=imgdata,
    labels=opts.get('labels'),
    width=opts.get('width'),
    title=opts.get('title'))
  return win


def images(images, **opts):
  # TODO: need to merge images into a single canvas
  raise Exception('Not implemented')


def plot(data, **opts):
  """ Plot data as line chart.
  Params:
    data: either a 2-d numpy array or a list of lists.
    win: pane id
    labels: list of series names, first series is always the X-axis
    see http://dygraphs.com/options.html for other supported options
  """
  win = opts.get('win') or uid()

  dataset = {}
  if type(data).__module__ == numpy.__name__:
    dataset = data.tolist()
  else:
    dataset = data

  # clone opts into options
  options = dict(opts)
  options['file'] = dataset
  if options.get('labels'):
    options['xlabel'] = options['labels'][0]

  # Don't pass our options to dygraphs.
  options.pop('win', None)

  send(command='plot', id=win, title=opts.get('title'), options=options)
  return win

