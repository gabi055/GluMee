import { View, Text, Button } from 'react-native';
import { signOut } from 'firebase/auth';
import { auth } from '../../../src/firebase';

export default function Perfil() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 }}>
      <Text>Perfil</Text>
      <Button title="Cerrar sesión" onPress={() => signOut(auth)} />
    </View>
  );
}