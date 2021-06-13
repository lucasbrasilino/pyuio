import random
from pyuio import UIODevices

if __name__ == '__main__':

	TEST_LOOP = 1000000000

	dev = UIODevices()

	print(f'found {len(dev)} usable UIO devices....')
	print('exercising uio1...')
	if not hasattr(dev,'uio1'):
		print('uio1 not found')
	else:
		for l in range(TEST_LOOP):
			idx = l % 16
			word = random.randint(0,0xFFFFFFFF)
			# Accessing registers using register index (from 0 up)
			dev.uio1.write_idx(idx,word)
			assert dev.uio1.read_idx(idx) == word

	print(f'exercising uio1 using its name and offset addressing...')
	offset = 0x0
	if not hasattr(dev,'gryphon_net'):
		print('uio1 not found')
	else:
		for l in range(TEST_LOOP):
			word = random.randint(0,0xFFFFFFFF)
			# Addressing registers using memory offset
			dev.gryphon_net.write_offset(offset,word)
			assert dev.gryphon_net.read_offset(offset) == word
			offset += 0x4

