export const VALIDATION_RULES = {
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: '请输入正确的邮箱格式（必须包含@）'
  },
  phone: {
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入正确的11位手机号码'
  }
}

export const validateEmail = (email) => {
  if (!email) return { valid: true, message: '' }
  const valid = VALIDATION_RULES.email.pattern.test(email)
  return {
    valid,
    message: valid ? '' : VALIDATION_RULES.email.message
  }
}

export const validatePhone = (phone) => {
  if (!phone) return { valid: true, message: '' }
  const valid = VALIDATION_RULES.phone.pattern.test(phone)
  return {
    valid,
    message: valid ? '' : VALIDATION_RULES.phone.message
  }
}
