import { describe, expect, it } from 'vitest'
import { buildGuestJoinUrl } from './guestSession'

describe('buildGuestJoinUrl', () => {
  it('builds /guest?code= and keeps an uppercase code', () => {
    expect(buildGuestJoinUrl('https://class.example.com', 'W9NN6X')).toBe(
      'https://class.example.com/guest?code=W9NN6X',
    )
  })

  it('strips a trailing slash from the origin', () => {
    expect(buildGuestJoinUrl('https://class.example.com/', 'W9NN6X')).toBe(
      'https://class.example.com/guest?code=W9NN6X',
    )
  })

  it('uppercases the access code', () => {
    expect(buildGuestJoinUrl('https://class.example.com', ' w9nn6x ')).toBe(
      'https://class.example.com/guest?code=W9NN6X',
    )
  })

  it('throws when origin or code is blank', () => {
    expect(() => buildGuestJoinUrl('', 'W9NN6X')).toThrow(
      'guest join url requires origin and code',
    )
    expect(() => buildGuestJoinUrl('https://class.example.com', '   ')).toThrow(
      'guest join url requires origin and code',
    )
  })
})
