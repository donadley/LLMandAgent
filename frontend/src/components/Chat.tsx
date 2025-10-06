import { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  Container,
  HStack,
} from '@chakra-ui/react';
import { useToaster } from './ui/toaster';
import { logger } from '../services/logger';
import axios from 'axios';

interface Message {
  text: string;
  isUser: boolean;
}

export const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const toast = useToaster();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim()) {
      logger.debug('Empty input, ignoring submission');
      return;
    }

    const userMessage = input;
    logger.info('Sending message to server', { message: userMessage });
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        text: userMessage,
      });

      logger.info('Received response from server', { 
        messageLength: response.data.response.length 
      });
      setMessages(prev => [...prev, { text: response.data.response, isUser: false }]);
    } catch (error) {
      logger.error('Failed to get response from server', { error });
      toast.create({
        title: 'Error',
        description: 'Failed to get response from the server',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
      logger.debug('Chat interaction completed');
    }
  };

  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={4} align="stretch" h="80vh">
        <Box flex={1} overflowY="auto" p={4} borderWidth={1} borderRadius="md">
          {messages.map((message, index) => (
            <Box
              key={index}
              bg={message.isUser ? 'blue.50' : 'gray.50'}
              p={3}
              borderRadius="md"
              mb={2}
              alignSelf={message.isUser ? 'flex-end' : 'flex-start'}
            >
              <Text>{message.text}</Text>
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Box>
        <HStack>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          />
          <Button
            colorScheme="blue"
            onClick={handleSubmit}
            isLoading={isLoading}
            loadingText="Sending..."
          >
            Send
          </Button>
        </HStack>
      </VStack>
    </Container>
  );
};