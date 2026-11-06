import '../../src/firebase';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { Stack, useRouter, useSegments } from 'expo-router';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '../../src/firebase';

export default function RootLayout() {
  // undefined = todavía comprobando la sesión guardada
  const [usuario, setUsuario] = useState<User | null | undefined>(undefined);
  const segmentos = useSegments();
  const router = useRouter();

  useEffect(() => onAuthStateChanged(auth, setUsuario), []);

  useEffect(() => {
    if (usuario === undefined) return;
    const enAuth = segmentos[0] === '(auth)';
    if (!usuario && !enAuth) router.replace('/(auth)/login');
    else if (usuario && enAuth) router.replace('/(tabs)');
  }, [usuario, segmentos]);

  if (usuario === undefined) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(tabs)" />
      <Stack.Screen name="(auth)" />
    </Stack>
  );
}