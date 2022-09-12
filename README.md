Ephyr Control
===

[Changelog](https://github.com/ALLATRA-IT/ephyr-control/blob/master/CHANGELOG.md)

Client library that allow to control [Ephyr] streaming.

## Overview
**Ephyr Control** is a set of tools to communicate with Ephyr server and manage its state.

It uses GraphQL for communication with Ephyr server. 
It supports synchronous `requests` transport for `query` and `mutation` operations, 
while asynchronous `websockets` transport is used for subscriptions.

### Example
 
See `examples/` folder for code examples.

## License

Ephyr Control is subject to the terms of the [Blue Oak Model License 1.0.0](https://github.com/ALLATRA-IT/ephyr/blob/master/LICENSE.md). If a copy of the [BlueOak-1.0.0](https://spdx.org/licenses/BlueOak-1.0.0.html) license was not distributed with this file, You can obtain one at <https://blueoakcouncil.org/license/1.0.0>.

As with all Docker images, these likely also contain other software which may be under other licenses (such as Bash, etc from the base distribution, along with any direct or indirect dependencies of the primary software being contained), including libraries used by [FFmpeg].

As for any pre-built image usage, it is the image user's responsibility to ensure that any use of this image complies with any relevant licenses for all software contained within.

# Creative Society

We strongly support the "Creative Society" project, and it's 8 fundamental values.

[Ephyr]: https://github.com/ALLATRA-IT/ephyr 
