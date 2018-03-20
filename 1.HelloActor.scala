/**
 * Created by X173213 on 19-03-2018.
 */
/*
1.You want to begin using actors to build concurrency into your applications.
 */

import akka.actor.{Actor,ActorSystem,Props}

/*
HelloActor’s behavior is implemented by defining a receive method, which is
implemented using a match expression.
 */
class HelloActor  extends Actor{
  def receive = {
    case "hello" => println("hello back at you")
    case _ => println("huh?")
  }
}


object HelloActor1 extends App{
  // an actor needs an ActorSystem
  val system = ActorSystem("HelloSystem")

  /* create and start the actor
    Actors can be created at the ActorSystem level, or inside other actors. At the
    ActorSystem level, actor instances are created with the system.actorOf method.
    An ActorSystem is the structure that allocates one or more threads for your application,
    so you typically create one ActorSystem per (logical) application.
  */
  val helloActor =system.actorOf(Props[HelloActor],name = "helloactor")
  /*
  When you call the actorOf method on an ActorSystem, it starts the actor asynchronously
  and returns an instance of an ActorRef. This reference is a “handle” to the actor,
  which you can think of as being a façade or broker between you and the actual actor.
  This façade keeps you from doing things that would break the Actor model, such as
  reaching into the Actor instance and attempting to directly mutate variables.
   */


  //send the actor 2 messages
  helloActor ! "hello"
  helloActor ! "bueno dias"

  system.shutdown()
}
