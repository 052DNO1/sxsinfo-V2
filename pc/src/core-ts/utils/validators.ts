/**
 * 密码验证工具
 */

interface PasswordStrengthResult {
  score: number
  percent: number
  label: string
  status: 'exception' | '' | 'success'
  className: 'weak' | 'medium' | 'good' | 'strong'
}

export const validatePasswordStrength = (pwd: string = ''): PasswordStrengthResult => {
  let score = 0
  if (pwd.length >= 8) score++
  if (/[a-z]/.test(pwd)) score++
  if (/[A-Z]/.test(pwd)) score++
  if (/[0-9]/.test(pwd)) score++
  
  const percent = [0, 25, 50, 75, 100][score]
  const label = score <= 1 ? '弱' : score === 2 ? '一般' : score === 3 ? '良好' : '很强'
  const status = score <= 1 ? 'exception' : score === 2 ? '' : 'success'
  const className = score <= 1 ? 'weak' : score === 2 ? 'medium' : score === 3 ? 'good' : 'strong'
  
  return { score, percent, label, status, className }
}

interface PasswordRequirements {
  length: boolean
  lowercase: boolean
  uppercase: boolean
  number: boolean
}

export const checkPasswordRequirements = (pwd: string = ''): PasswordRequirements => {
  return {
    length: pwd.length >= 8,
    lowercase: /[a-z]/.test(pwd),
    uppercase: /[A-Z]/.test(pwd),
    number: /[0-9]/.test(pwd)
  }
}
