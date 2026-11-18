import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Without Vitest globals, RTL cannot auto-register cleanup — unmount each
// test's rendered tree ourselves so tests don't see each other's DOM.
afterEach(cleanup)
