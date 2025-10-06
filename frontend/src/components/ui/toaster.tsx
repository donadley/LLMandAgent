import { useToast, type UseToastOptions } from '@chakra-ui/react'

type ToastStatus = 'info' | 'warning' | 'success' | 'error'

interface ToastParams {
  title: string;
  description?: string;
  status?: ToastStatus;
  duration?: number;
  isClosable?: boolean;
}

export const useToaster = () => {
  const toast = useToast()

  return {
    create: ({
      title,
      description,
      status = 'info',
      duration = 3000,
      isClosable = true
    }: ToastParams) => {
      toast({
        title,
        description,
        status,
        duration,
        isClosable,
        position: 'bottom'
      })
    }
  }
}

export const toaster = {
  create: (options: UseToastOptions | undefined) => {
    const toast = useToast()
    toast({
      ...options,
      position: 'bottom',
      duration: 3000,
      isClosable: true
    })
  }
}