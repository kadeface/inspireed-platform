import { describe, expect, it } from 'vitest'
import { buildGuestJoinUrl, guestJoinOrigin } from './guestSession'

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

  it('replaces a loopback host with the LAN address and keeps the port', () => {
    expect(guestJoinOrigin('http://127.0.0.1:5173', '192.168.1.20')).toBe(
      'http://192.168.1.20:5173',
    )
    expect(guestJoinOrigin('http://localhost:5173/', ' 10.0.0.8 ')).toBe('http://10.0.0.8:5173')
  })

  it('keeps a domain or an address that phones can already open', () => {
    expect(guestJoinOrigin('https://class.example.com', '192.168.1.20')).toBe(
      'https://class.example.com',
    )
    expect(guestJoinOrigin('http://192.168.1.20:5173', '10.0.0.8')).toBe(
      'http://192.168.1.20:5173',
    )
  })

  it('keeps loopback when no LAN address is available', () => {
    expect(guestJoinOrigin('http://127.0.0.1:5173', null)).toBe('http://127.0.0.1:5173')
    expect(guestJoinOrigin('http://127.0.0.1:5173', '   ')).toBe('http://127.0.0.1:5173')
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
