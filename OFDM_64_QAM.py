#!/usr/bin/env python
# coding: utf-8

# In[20]:



import numpy as np
import scipy.interpolate
import scipy
import matplotlib.pyplot as plt

S_Power = 0
N_Power = 0

def get_ber(K, CP, P, SNRdb):
  pilotValue = 7+7j 
  allCarriers = np.arange(K)  

  pilotCarriers = allCarriers[::K//P] 


  pilotCarriers = np.hstack([pilotCarriers, np.array([allCarriers[-1]])])
  P = P+1


  dataCarriers = np.delete(allCarriers, pilotCarriers)
  print ("allCarriers:   %s" % allCarriers)
  print ("pilotCarriers: %s" % pilotCarriers)
  print ("dataCarriers:  %s" % dataCarriers)
  #plt.plot(pilotCarriers, np.zeros_like(pilotCarriers), 'bo', label='pilot', markersize=5)
  #plt.plot(dataCarriers, np.zeros_like(dataCarriers), 'ro', label='data', markersize=5)


  mu = 6 # bits per symbol (i.e. 64-QAM)
  payloadBits_per_OFDM = len(dataCarriers)*mu  # number of payload bits per OFDM symbol

  mapping_table = {
  (0,0,0,0,0,0) : +7+7j,
  (0,0,0,0,0,1) : +5+7j,
  (0,0,0,0,1,0) : +1+7j,
  (0,0,0,0,1,1) : +3+7j,
  (0,0,0,1,0,0) : -7+7j,
  (0,0,0,1,0,1) : -5+7j,
  (0,0,0,1,1,0) : -1+7j,
  (0,0,0,1,1,1) : -3+7j,
  (0,0,1,0,0,0) : +7+5j,
  (0,0,1,0,0,1) : +5+5j,
  (0,0,1,0,1,0) : +1+5j,
  (0,0,1,0,1,1) : +3+5j,
  (0,0,1,1,0,0) : -7+5j,
  (0,0,1,1,0,1) : -5+5j,
  (0,0,1,1,1,0) : -1+5j,
  (0,0,1,1,1,1) : -3+5j,#00
  (0,1,0,0,0,0) : +7+1j,
  (0,1,0,0,0,1) : +5+1j,
  (0,1,0,0,1,0) : +1+1j,
  (0,1,0,0,1,1) : +3+1j,
  (0,1,0,1,0,0) : -7+1j,
  (0,1,0,1,0,1) : -5+1j,
  (0,1,0,1,1,0) : -1+1j,
  (0,1,0,1,1,1) : -3+1j,
  (0,1,1,0,0,0) : +7+3j,
  (0,1,1,0,0,1) : +5+3j,
  (0,1,1,0,1,0) : +1+3j,
  (0,1,1,0,1,1) : +3+3j,
  (0,1,1,1,0,0) : -7+3j,
  (0,1,1,1,0,1) : -5+3j,
  (0,1,1,1,1,0) : -1+3j,
  (0,1,1,1,1,1) : -3+3j,# 10
  (1,0,0,0,0,0) : +7-7j,
  (1,0,0,0,0,1) : +5-7j,
  (1,0,0,0,1,0) : +1-7j,
  (1,0,0,0,1,1) : +3-7j,
  (1,0,0,1,0,0) : -7-7j,
  (1,0,0,1,0,1) : -5-7j,
  (1,0,0,1,1,0) : -1-7j,
  (1,0,0,1,1,1) : -3-7j,
  (1,0,1,0,0,0) : +7-5j,
  (1,0,1,0,0,1) : +5-5j,
  (1,0,1,0,1,0) : +1-5j,
  (1,0,1,0,1,1) : +3-5j,
  (1,0,1,1,0,0) : -7-5j,
  (1,0,1,1,0,1) : -5-5j,
  (1,0,1,1,1,0) : -1-5j,
  (1,0,1,1,1,1) : -3-5j,#11
  (1,1,0,0,0,0) : +7-1j,
  (1,1,0,0,0,1) : +5-1j,
  (1,1,0,0,1,0) : +1-1j,
  (1,1,0,0,1,1) : +3-1j,
  (1,1,0,1,0,0) : -7-1j,
  (1,1,0,1,0,1) : -5-1j,
  (1,1,0,1,1,0) : -1-1j,
  (1,1,0,1,1,1) : -3-1j,
  (1,1,1,0,0,0) : +7-3j,
  (1,1,1,0,0,1) : +5-3j,
  (1,1,1,0,1,0) : +1-3j,
  (1,1,1,0,1,1) : +3-3j,
  (1,1,1,1,0,0) : -7-3j,
  (1,1,1,1,0,1) : -5-3j,
  (1,1,1,1,1,0) : -1-3j,
  (1,1,1,1,1,1) : -3-3j
  }
  for b5 in [0, 1]:
   for b4 in [0, 1]:
    for b3 in [0, 1]:
     for b2 in [0, 1]:
      for b1 in [0, 1]:
        for b0 in [0, 1]:
            B = (b5,b4,b3, b2, b1, b0)
            Q = mapping_table[B]
            plt.figure(1)
            plt.plot(Q.real, Q.imag, 'go')
            plt.text(Q.real, Q.imag+0.2, "".join(str(x) for x in B), ha='center')

  #plt.plot(Q.real, Q.imag, 'go',label='Correct 64-QAM points')
  #plt.grid(True)
  #plt.ylim(-12)    

  channelResponse = np.array([1, 0,0.5+0.5j])  # the impulse response of the wireless channel
  #print(channelResponse)
  H_exact = np.fft.fft(channelResponse, K)
  #print(H_exact)
  #plt.plot(allCarriers, abs(H_exact))
  #plt.plot(allCarriers, abs(H_exact),'.-',label='Channel frequency Response')
  #plt.xlabel('Carrier index'); plt.ylabel('$|H(f)|$'); plt.legend(fontsize=10)
  #plt.ylim(0,3)


  bits = np.random.binomial(n=1, p=0.5, size=(payloadBits_per_OFDM, ))
  print ("Bits count: ", len(bits))
  #print ("First 20 bits: ", bits[:64])
  print ("Mean of bits (should be around 0.5): ", np.mean(bits))
  mu=6 # 6 bits per symbol
  def SP(bits):
    return bits.reshape((len(dataCarriers), mu))

  bits_SP = SP(bits)
  #print ("16 bit groups")
  #print (bits_SP[:16,:])

  def Mapping(bits):
    return np.array([mapping_table[tuple(b)] for b in bits])
  QAM = Mapping(bits_SP)
  #print ("First 16 QAM symbols and bits:")
  #print (bits_SP[:16,:])
  #print (QAM[:16])
  demapping_table = {v : k for k, v in mapping_table.items()}

  def OFDM_symbol(QAM_payload):
    symbol = np.zeros(K, dtype=complex) # the overall K subcarriers
    symbol[pilotCarriers] = pilotValue  # allocate the pilot subcarriers 
    symbol[dataCarriers] = QAM_payload  # allocate the pilot subcarriers
    return symbol
  OFDM_data = OFDM_symbol(QAM)
  print ("Number of OFDM carriers in frequency domain: ", len(OFDM_data))

  def IFFT(OFDM_data):
    return np.fft.ifft(OFDM_data)
  OFDM_time = IFFT(OFDM_data)
  print ("Number of OFDM samples in time-domain before CP: ", len(OFDM_time))

  def addCP(OFDM_time):
    cp = OFDM_time[-CP:]               # take the last CP samples ...
    return np.hstack([cp, OFDM_time])  # ... and add them to the beginning
  OFDM_withCP = addCP(OFDM_time)
  print ("Number of OFDM samples in time domain with CP: ", len(OFDM_withCP))

  def channel(signal):
    convolved = np.convolve(signal, channelResponse)
    signal_power = np.mean(abs(convolved**2))
    sigma2 = signal_power * 10**(-SNRdb/10)  # calculate noise power based on signal power and SNR
    print ("RX Signal power: %.4f. Noise power: %.4f" % (signal_power, sigma2))
    global S_Power
    S_Power = signal_power
    global N_Power
    N_Power = sigma2
    # Generate complex noise with given variance
    noise = np.sqrt(sigma2/2) * (np.random.randn(*convolved.shape)+1j*np.random.randn(*convolved.shape))
    return convolved + noise
  OFDM_TX = OFDM_withCP
  OFDM_RX = channel(OFDM_TX)
  plt.figure(figsize=(15,4))
  plt.plot(abs(OFDM_TX), label='TX signal', color='green')
  plt.plot(abs(OFDM_RX), label='RX signal',color='red')
  plt.legend(fontsize=10)
  plt.xlabel('Time'); plt.ylabel('$|x(t)|$');
  plt.grid(True);

  def removeCP(signal):
    return signal[CP:(CP+K)]
  OFDM_RX_noCP = removeCP(OFDM_RX)

  def FFT(OFDM_RX):
    return np.fft.fft(OFDM_RX)
  OFDM_demod = FFT(OFDM_RX_noCP)

  def channelEstimate(OFDM_demod):
    pilots = OFDM_demod[pilotCarriers]  # extract the pilot values from the RX signal
    Hest_at_pilots = pilots / pilotValue # divide by the transmitted pilot values

    # Perform interpolation between the pilot carriers to get an estimate
    # of the channel in the data carriers. Here, we interpolate absolute value and phase 
    # separately
    Hest_abs = scipy.interpolate.interp1d(pilotCarriers, abs(Hest_at_pilots), kind='linear')(allCarriers)
    Hest_phase = scipy.interpolate.interp1d(pilotCarriers, np.angle(Hest_at_pilots), kind='linear')(allCarriers)
    Hest = Hest_abs * np.exp(1j*Hest_phase)

    #plt.plot(allCarriers, abs(H_exact), label='Correct Channel')
    #plt.stem(pilotCarriers, abs(Hest_at_pilots), label='Pilot estimates')
    #plt.plot(allCarriers, abs(Hest), label='Estimated channel via interpolation')
    #plt.grid(True); plt.xlabel('Carrier index'); plt.ylabel('$|H(f)|$'); plt.legend(fontsize=10)
    #plt.ylim(0,3)
    return Hest

  Hest = channelEstimate(OFDM_demod)

  def equalize(OFDM_demod, Hest):
    return OFDM_demod / Hest
  equalized_Hest = equalize(OFDM_demod, Hest)

  def get_payload(equalized):
    return equalized[dataCarriers]

  #QAM_est_before_equ = get_payload(OFDM_demod)
  #plt.plot(QAM_est_before_equ.real, QAM_est_before_equ.imag, 'ro',label='Before Equalization');
  QAM_est = get_payload(equalized_Hest)
  #plt.plot(QAM_est.real, QAM_est.imag, 'bo',label='After Equalization');
  #plt.legend(fontsize=8)

  def Demapping(QAM):
    # array of possible constellation points
    constellation = np.array([x for x in demapping_table.keys()])
    # calculate distance of each RX point to each possible point
    dists = abs(QAM.reshape((-1,1)) - constellation.reshape((1,-1)))
    # for each element in QAM, choose the index in constellation 
    # that belongs to the nearest constellation point
    const_index = dists.argmin(axis=1)
    # get back the real constellation point
    hardDecision = constellation[const_index]
    # transform the constellation point into the bit groups
    return np.vstack([demapping_table[C] for C in hardDecision]), hardDecision

  PS_est, hardDecision = Demapping(QAM_est)
  plt.figure(3)
  for qam, hard in zip(QAM_est, hardDecision):
    plt.plot([qam.real, hard.real], [qam.imag, hard.imag], 'b-o');
    plt.plot(hardDecision.real, hardDecision.imag, 'go')
  plt.grid(True)
  #print(bits_est)
  def PS(bits):
    return bits.reshape((-1,))
  bits_est = PS(PS_est)
  #print(bits_est)
  print ("Obtained Bit error rate: ", np.sum(abs(bits-bits_est))/len(bits))
  x = {
    "N_Power": N_Power, 
    "S_Power": S_Power, 
    "BER": np.sum(abs(bits-bits_est))/len(bits)
  }
  return x



  # In[ ]:




