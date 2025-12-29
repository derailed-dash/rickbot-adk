import * as React from 'react';
import Head from 'next/head';
import Chat from '../components/Chat';

export default function Home() {
  return (
    <>
      <Head>
        <title>Rickbot</title>
        <meta name="description" content="Rickbot Chatbot" />
        <link rel="icon" href="/avatars/rick.png" />
      </Head>
      <Chat />
    </>
  );
}
