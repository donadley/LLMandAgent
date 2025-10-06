import { ChakraProvider, Box, Heading } from '@chakra-ui/react'
import { Chat } from './components/Chat'
import { toaster } from './components/ui/toaster'

function App() {
  return (
    <ChakraProvider>
      <Box textAlign="center" py={4}>
        <Heading mb={6}>LLM Chat Interface</Heading>
        <Chat />
      </Box>
    </ChakraProvider>
  )
}

export default App
