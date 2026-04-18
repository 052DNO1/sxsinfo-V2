/**
 * 验证密码强度
 * @param {string} pwd - 密码
 * @returns {object} 包含分数、标签、状态、类名和百分比的对象
 */
export const validatePasswordStrength = (pwd) => {
  if (!pwd) pwd = ''
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

/**
 * 验证密码是否满足要求
 * @param {string} pwd - 密码
 * @returns {object} 各项要求是否满足的布尔值对象
 */
export const checkPasswordRequirements = (pwd) => {
  if (!pwd) pwd = ''
  return {
    length: pwd.length >= 8,
    lowercase: /[a-z]/.test(pwd),
    uppercase: /[A-Z]/.test(pwd),
    number: /[0-9]/.test(pwd)
  }
}
