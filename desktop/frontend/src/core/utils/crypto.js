import CryptoJS from 'crypto-js'

const SECRET_KEY = import.meta.env.VITE_PASSWORD_ENCRYPT_KEY || ''
const ENABLE_ENCRYPT = !!SECRET_KEY

export function encryptPassword(password) {
  if (!password) return ''
  
  if (!ENABLE_ENCRYPT) {
    return password
  }
  
  const timestamp = Date.now().toString()
  const timeHex = timestamp.toString(16).padStart(16, '0')
  const iv = CryptoJS.enc.Utf8.parse(timeHex.substring(0, 16))
  
  const key = CryptoJS.enc.Utf8.parse(SECRET_KEY.padEnd(32, '0').substring(0, 32))
  
  const encrypted = CryptoJS.AES.encrypt(password, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  })
  
  return timeHex + ':' + encrypted.ciphertext.toString(CryptoJS.enc.Base64)
}

export function decryptPassword(encryptedData) {
  if (!encryptedData || !encryptedData.includes(':')) {
    return encryptedData
  }
  
  if (!ENABLE_ENCRYPT) {
    return encryptedData
  }
  
  try {
    const [timeHex, encryptedBase64] = encryptedData.split(':')
    const iv = CryptoJS.enc.Utf8.parse(timeHex.substring(0, 16))
    
    const key = CryptoJS.enc.Utf8.parse(SECRET_KEY.padEnd(32, '0').substring(0, 32))
    
    const decrypted = CryptoJS.AES.decrypt(encryptedBase64, key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    })
    
    return decrypted.toString(CryptoJS.enc.Utf8)
  } catch (e) {
    return null
  }
}

export function isEncryptionEnabled() {
  return ENABLE_ENCRYPT
}
