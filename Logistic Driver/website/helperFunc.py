import tensorflow as tf
#physical_devices = tf.config.experimental.list_physical_devices("GPU") #Check available GPUs
#tf.config.experimental.set_memory_growth(physical_devices[0], True)
from matplotlib import pyplot
from PIL import Image
from numpy import asarray
from scipy.spatial.distance import cosine
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import numpy as np

# extract a single face from a given photograph
def extract_face(filename, required_size=(224, 224)):
	# load image from file
	pixels = pyplot.imread(filename)
	# create the detector, using default weights
	detector = MTCNN()
	# detect faces in the image
	results = detector.detect_faces(pixels)
	# extract the bounding box from the first face if exists
	if results:
		x1, y1, width, height = results[0]['box']
		
		x2, y2 = x1 + width, y1 + height
		# extract the face
		face = pixels[y1:y2, x1:x2]
		# resize pixels to the model size
		image = Image.fromarray(face)
		image = image.resize(required_size)
		face_array = asarray(image)
		return face_array
	else:
		return pixels

# extract faces and calculate face embeddings for the photo
def get_embeddings(filename):
	# extract faces
	faces = [extract_face(f) for f in filename]
	# convert into an array of samples
	samples = asarray(faces, 'float32')
	# prepare the face for the model, e.g. center pixels
	samples = preprocess_input(samples, version=2)
	# create a vggface model
	model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
	# perform prediction
	yhat = model.predict(samples)
	return yhat

# determine if a candidate face is a match for a known face
def is_match(known_embedding, candidate_embedding, thresh=0.3):
	# calculate distance between embeddings
	score = cosine(known_embedding, candidate_embedding)
	#If score is less than the threshold, it means the distance between embeddings is very small and it is a match
	if score <= thresh:
		return True
	else:
		return False

def encFromByte(byteEnc):
	#Convert Image Bytes stored in database back to image encoding
	orgEnc = np.frombuffer(byteEnc,dtype=np.float32)
	return orgEnc